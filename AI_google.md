你的 Dockerfile 中已经包含了 `RUN apt-get install -y fish`，要将其设置为**默认 Shell**，主要是添加 `chsh` 命令。

此外，由于 `uv` 的安装脚本通常默认只配置 bash/sh 的环境变量，为了让 `uv` 命令在 fish 终端中也能直接使用，建议显式添加环境变量配置。

以下是修改后的 Dockerfile，我优化了指令顺序以减小镜像体积，并添加了相关的配置：

```dockerfile
FROM ubuntu:22.04

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
    fish

# 设置 MPV 软链接
RUN ln -s /usr/lib/x86_64-linux-gnu/libmpv.so /usr/lib/libmpv.so.1

# 安装 UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# --- 关键修改点开始 ---

# 1. 设置 fish 为 root 用户的默认 Shell
RUN chsh -s /usr/bin/fish root

# 2. 设置环境变量
# uv 通常安装在 /root/.local/bin 或 /root/.cargo/bin
# 我们将其加入 PATH，这样在 fish 中也能直接使用 uv 命令
ENV PATH="/root/.local/bin:/root/.cargo/bin:$PATH"

# 3. (可选) 配置 fish 不显示欢迎语，让终端更清爽
RUN mkdir -p /root/.config/fish && \
    echo "set -g fish_greeting" >> /root/.config/fish/config.fish

# --- 关键修改点结束 ---

RUN mkdir /codex

RUN mkdir /var/run/sshd

RUN echo "root:929123" | chpasswd

RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config

# 清理缓存放在最后
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 22

# --- 6. 设置容器启动命令和健康检查 ---
HEALTHCHECK --interval=30s --timeout=5s CMD ps aux | grep "[s]shd -D" || exit 1

CMD ["/usr/sbin/sshd", "-D"]
```

### 修改说明：

1.  **`RUN chsh -s /usr/bin/fish root`**: 这是将默认 Shell 更改为 fish 的核心命令。当你通过 SSH 登录时，系统会检查 `/etc/passwd`，这条命令会修改该文件，将 root 的 shell 指向 fish。
2.  **`ENV PATH="..."`**: `uv` 的安装脚本通常修改 `.bashrc` 或 `.profile`，但 fish 不读取这些文件。通过 Docker 的 `ENV` 指令设置全局 PATH，可以确保无论进入哪种 Shell，`uv` 命令都能被找到。
3.  **合并 `apt-get install`**: 我将 `fish` 的安装合并到了前面的 `apt-get` 块中。这是一种 Docker 最佳实践，可以减少镜像层数（Layer），加快构建速度并略微减小体积。

### 如何验证？
构建并运行容器后，通过 SSH 登录，你应该会看到类似以下的 Fish 提示符（彩色），而不是黑白的 `#`：

```text
root@container_id ~>
```
---
使用 Podman 构建 Dockerfile 与使用 Docker 非常相似，几乎是命令上的直接替换。

假设你的 Dockerfile 文件名为 `Dockerfile`，并且位于当前目录。

### 1. 基本构建命令

在终端中运行以下命令：

```bash
podman build -t my-ssh-image .
```

*   **`podman build`**: 构建镜像的命令。
*   **`-t my-ssh-image`**: 给构建出来的镜像起个名字叫 `my-ssh-image`（即 tag）。
*   **`.`**: 指示 Podman 在当前目录寻找 `Dockerfile`。

### 2. 运行并测试容器

构建成功后，你可以运行这个镜像来测试 SSH 和 fish 终端是否生效：

```bash
# 启动容器，将宿主机的 2222 端口映射到容器的 22 端口
podman run -d -p 2222:22 --name my-ssh-container my-ssh-image

# 测试 SSH 连接 (密码是 Dockerfile 里设置的 929123)
ssh root@localhost -p 2222
```

登录成功后，你应该直接进入 **fish** 终端环境。

### 3. 常见问题处理 (Podman 特有)

Podman 是**无守护进程 (Daemonless)** 且默认为 **rootless (非 root 用户运行)** 的。这在构建包含 `apt-get` 等系统级操作的 Dockerfile 时通常没问题，但有时可能会遇到权限问题。

**如果你在构建过程中遇到“权限拒绝 (Permission denied)”或“无法解析主机”的错误：**

1.  **加上 `--format docker` 参数（推荐）**：
    Podman 默认使用 OCI 标准构建，有时 Dockerfile 的某些指令更兼容 Docker 格式。
    ```bash
    podman build --format docker -t my-ssh-image .
    ```

2.  **网络问题**：
    如果 `apt-get update` 或 `curl` 失败，尝试添加 `--network host`：
    ```bash
    podman build --network host -t my-ssh-image .
    ```

3.  **Rootless 模式下的端口绑定**：
    如果你是以普通用户运行 `podman run`，你可能无法绑定低端口（如 22）。这就是为什么上面的例子使用了 `-p 2222:22` 而不是 `-p 22:22`。普通用户通常只能绑定 1024 以上的端口。

### 总结
简单来说，把所有你会用的 `docker build ...` 命令中的 `docker` 换成 `podman` 即可，参数基本通用。na