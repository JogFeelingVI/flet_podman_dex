# syntax=docker/dockerfile:1
FROM debian:bookworm-slim

# Build args
ARG DEBIAN_FRONTEND=noninteractive
ARG SSH_PASSWORD=code123456

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_CACHE_DIR=/root/.cache/uv \
    PATH="/usr/local/bin:/root/.local/bin:/root/.cargo/bin:$PATH"

# Copy uv from the official image (no network download, no intermediate layer)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install system dependencies, set up MPV symlink, configure SSH and locale
# in a single RUN so no intermediate layers are produced.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
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
        locales; \
    sed -i 's/^# *en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen; \
    locale-gen; \
    apt-get autoremove -y; \
    apt-get clean -y; \
    rm -rf /usr/include /usr/share/doc /usr/share/man /usr/lib/x86_64-linux-gnu/*.a; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
        amd64) multiarch="x86_64-linux-gnu" ;; \
        arm64) multiarch="aarch64-linux-gnu" ;; \
        *) multiarch="${arch}-linux-gnu" ;; \
    esac; \
    ln -sf "/usr/lib/${multiarch}/libmpv.so.2" /usr/lib/libmpv.so.1; \
    mkdir -p /var/run/sshd /codex; \
    echo "root:${SSH_PASSWORD}" | chpasswd; \
    printf 'PermitRootLogin yes\nUseDNS no\nPrintLastLog no\n' >> /etc/ssh/sshd_config; \
    touch /root/.hushlogin; \
    sed -i 's/^\s*session\s\+optional\s\+pam_motd.so/# &/' /etc/pam.d/sshd; \
    printf 'export PATH="/usr/local/bin:/root/.local/bin:/root/.cargo/bin:$PATH"\n' > /etc/profile.d/uv.sh; \
    chmod +x /etc/profile.d/uv.sh

# Mount the uv cache to a host directory or Docker volume at runtime
VOLUME ["/root/.cache/uv"]

WORKDIR /codex

EXPOSE 22

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD pgrep -x sshd >/dev/null || exit 1

CMD ["/usr/sbin/sshd", "-D"]