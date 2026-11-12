FROM debian:bookworm-slim

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
        libmpv2 \
        fish \
        locales \
    && sed -i 's/^# *en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen \
    && locale-gen \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* \
        /usr/include \
        /usr/share/doc \
        /usr/share/man \
        /usr/lib/x86_64-linux-gnu/*.a

# Set up MPV symlink (arch-independent): app expects libmpv.so.1, bookworm ships libmpv.so.2
RUN arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
        amd64) multiarch="x86_64-linux-gnu" ;; \
        arm64) multiarch="aarch64-linux-gnu" ;; \
        *) multiarch="${arch}-linux-gnu" ;; \
    esac; \
    ln -sf "/usr/lib/${multiarch}/libmpv.so.2" /usr/lib/libmpv.so.1

# Install uv (explicit download so network failures abort the build)
RUN set -eux; \
    curl -fsSL --retry 3 --retry-delay 2 https://astral.sh/uv/install.sh -o /tmp/uv-install.sh; \
    sh /tmp/uv-install.sh; \
    rm -f /tmp/uv-install.sh; \
    /root/.local/bin/uv --version

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
