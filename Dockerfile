FROM ubuntu:22.04

# Build args
ARG DEBIAN_FRONTEND=noninteractive
ARG SSH_PASSWORD=code123456

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:/root/.cargo/bin:$PATH"

# Install system dependencies in a single layer and clean up in the same step
RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server \
        curl \
        git \
        ca-certificates \
        libgstreamer1.0-0 \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad \
        gstreamer1.0-plugins-ugly \
        gstreamer1.0-libav \
        gstreamer1.0-tools \
        libmpv-dev \
        fish \
        locales \
    && locale-gen en_US.UTF-8 \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Set up MPV symlink (arch-independent)
RUN arch="$(dpkg-architecture -qDEB_HOST_GNU_CPU 2>/dev/null || echo x86_64)"; \
    ln -sf "/usr/lib/${arch}-linux-gnu/libmpv.so" /usr/lib/libmpv.so.1

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Configure fish (no greeting) + make uv visible in login shells (ssh/VS Code)
RUN mkdir -p /root/.config/fish /etc/profile.d \
    && printf 'set -g fish_greeting\n' >> /root/.config/fish/config.fish \
    && printf 'fish_add_path /root/.local/bin /root/.cargo/bin\n' >> /root/.config/fish/config.fish \
    && printf 'export PATH="/root/.local/bin:/root/.cargo/bin:$PATH"\n' > /etc/profile.d/uv.sh \
    && chmod +x /etc/profile.d/uv.sh

# SSH setup
RUN mkdir -p /var/run/sshd /codex \
    && echo "root:${SSH_PASSWORD}" | chpasswd \
    && printf 'PermitRootLogin yes\nUseDNS no\nPrintLastLog no\n' >> /etc/ssh/sshd_config \
    && touch /root/.hushlogin \
    && sed -i 's/^\s*session\s\+optional\s\+pam_motd.so/# &/' /etc/pam.d/sshd

# Auto-switch to fish for interactive shells (except VS Code remote)
RUN printf "if [[ \$- == *i* ]] && [[ \"\$TERM_PROGRAM\" != \"vscode\" ]]; then exec fish; fi\n" >> /root/.bashrc

WORKDIR /codex

EXPOSE 22

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD pgrep -x sshd >/dev/null || exit 1

CMD ["/usr/sbin/sshd", "-D"]
