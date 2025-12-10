FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
# 为了减少镜像层数，建议将 apt install 合并，把 fish 加在这里
RUN apt-get update && apt-get install -y \
    openssh-server \
    curl \
    git \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    libmpv-dev \
    fish \
    locales

# 设置 MPV 软链接
RUN ln -s /usr/lib/x86_64-linux-gnu/libmpv.so /usr/lib/libmpv.so.1

# 安装 UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh



# 2. 设置环境变量
# uv 通常安装在 /root/.local/bin 或 /root/.cargo/bin
# 我们将其加入 PATH，这样在 fish 中也能直接使用 uv 命令
ENV PATH="/root/.local/bin:/root/.cargo/bin:$PATH"

# 3. (可选) 配置 fish 不显示欢迎语，让终端更清爽
RUN mkdir -p /root/.config/fish && \
    echo "set -g fish_greeting" >> /root/.config/fish/config.fish

# --- 关键修改点结束 ---

RUN mkdir /codex

# 3. 配置 SSH 服务
RUN mkdir /var/run/sshd
# 设置 root 密码 (请根据需要修改)
RUN echo 'root:my_secure_password' | chpasswd
# 允许 root 远程登录
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
# 禁止 SSH DNS 解析，加快连接速度
RUN echo 'UseDNS no' >> /etc/ssh/sshd_config

# --- 屏蔽 SSH 登录后的欢迎信息 (关键修复 VS Code 连接超时) ---

# 1. 创建 .hushlogin 文件
RUN touch /root/.hushlogin

# 2. 修改 PAM 配置，彻底禁用 motd (Message of the Day) 打印
# 这两行 sed 命令会把 /etc/pam.d/sshd 文件里涉及 motd 的行注释掉
RUN sed -i 's/^\s*session\s\+optional\s\+pam_motd.so/# &/' /etc/pam.d/sshd

# 3. 禁止 SSH 显示 "Last login" 信息
RUN sed -i 's/^PrintLastLog yes/PrintLastLog no/' /etc/ssh/sshd_config

RUN echo 'if [[ $- == *i* ]] && [[ "$TERM_PROGRAM" != "vscode" ]]; then exec fish; fi' >> /root/.bashrc

# 配置 Locale (防止终端乱码)
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# 6. 配置工作目录
WORKDIR /codex
# 清理缓存放在最后
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 22

# --- 6. 设置容器启动命令和健康检查 ---
HEALTHCHECK --interval=30s --timeout=5s CMD ps aux | grep "[s]shd -D" || exit 1

CMD ["/usr/sbin/sshd", "-D"]