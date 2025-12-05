FROM ubuntu:22.04

RUN apt-get update && apt-get install -y openssh-server curl git

RUN apt-get install -y libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools

RUN apt-get install -y libmpv-dev

RUN ln -s /usr/lib/x86_64-linux-gnu/libmpv.so /usr/lib/libmpv.so.1

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN apt-get install -y fish

RUN curl -L https://get.oh-my.fish > install_omf && \
    fish install_omf --noninteractive && \
    rm install_omf

SHELL ["/usr/bin/fish", "-c"]

RUN mkdir /codex

RUN mkdir /var/run/sshd

RUN echo "root:929123" | chpasswd

RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config

RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 22

# --- 6. 设置容器启动命令和健康检查 (无变化) ---
HEALTHCHECK --interval=30s --timeout=5s CMD ps aux | grep "[s]shd -D" || exit 1

CMD ["/usr/sbin/sshd", "-D"]
