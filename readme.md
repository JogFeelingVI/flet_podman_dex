这份 Wiki 文档旨在帮助团队成员或使用者快速理解该 Docker镜像的功能、构建方法以及使用方式。

---

# 🐳 Codex Development Environment (Ubuntu 22.04 + SSH + Multimedia + UV)

## 📖 简介 (Overview)

这是一个基于 `Ubuntu 22.04` 构建的高级开发环境镜像。它专为 **VS Code Remote - SSH** 开发模式优化，集成了现代化的 Python 包管理工具 `uv`、强大的多媒体处理库 (GStreamer/MPV) 以及友好的交互式 Shell (Fish)。

该镜像特别解决了 VS Code 远程连接时的超时和协议冲突问题，是一个开箱即用的多媒体/Python 开发沙盒。

## ✨ 核心特性 (Features)

*   **基础系统**: Ubuntu 22.04 LTS (Jammy Jellyfish).
*   **开发工具**:
    *   `git`, `curl`, `openssh-server`.
    *   **Python 工具链**: 集成 [astral.sh/uv](https://github.com/astral-sh/uv)，超高速 Python 包管理器。
*   **多媒体支持**:
    *   全套 **GStreamer** 插件 (base, good, bad, ugly, libav, tools).
    *   **libmpv** 开发库 (包含软链接修复).
*   **终端体验**:
    *   预装 **Fish Shell**，且配置为登录后自动切换（保留 Bash 兼容性）。
    *   UTF-8 Locale 配置，防止中文乱码。
*   **SSH & VS Code 优化**:
    *   禁用了 MOTD (每日消息)、Last Login 和 DNS 解析，极速连接。
    *   修复了 VS Code Remote 因欢迎信息过长导致的连接挂起问题。

---

## 🛠️ 构建指南 (Build Instructions)

将提供的 `Dockerfile` 保存到当前目录，运行以下命令构建镜像：

```bash
# 构建镜像，标签为 codex-dev:latest
docker build -t codex-dev:latest .
```

---

## 🚀 启动容器 (Usage)

### 1. 启动容器
启动容器并将容器内的 SSH 端口 (22) 映射到宿主机的端口 (例如 2222)：

```bash
docker run -d \
  --name codex-container \
  -p 2222:22 \
  -v $(pwd)/workspace:/codex \
  codex-dev:latest
```
*   `-p 2222:22`: 将宿主机的 2222 端口转发到容器的 SSH。
*   `-v ...`: (可选) 将本地代码目录挂载到容器内的 `/codex`。

### 2. SSH 连接信息
*   **用户名**: `root`
*   **默认密码**: `my_secure_password` (⚠️ **注意**: 仅限开发环境，生产环境请修改 Dockerfile)
*   **端口**: 映射的端口 (如 2222)

### 3. 使用 VS Code 连接
在本地机器的 `~/.ssh/config` 文件中添加以下配置，即可通过 VS Code 的 Remote-SSH 插件一键连接：

```ssh
Host codex-dev
    HostName localhost
    User root
    Port 2222
    # 防止因容器重建导致指纹变化报错
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

---

## ⚙️ 关键配置详解 (Configuration Details)

### Python 环境 (UV)
*   `uv` 安装路径: `/root/.local/bin` 或 `/root/.cargo/bin`。
*   环境变量 `PATH` 已更新，在 Bash 和 Fish 中均可直接使用 `uv` 命令。

### Shell 行为 (Bash -> Fish)
Dockerfile 包含以下逻辑：
```bash
if [[ $- == *i* ]] && [[ "$TERM_PROGRAM" != "vscode" ]]; then exec fish; fi
```
*   **原理**: 当你通过终端 (Terminal) SSH 登录时，系统会自动切换到 `fish` shell 以提供更好的交互体验。
*   **VS Code 特例**: 当 VS Code 后台连接时 (`TERM_PROGRAM=vscode`)，保持使用 `bash`，这能防止 VS Code 的自动脚本因不兼容 Fish 语法而报错。

### VS Code 连接修复 (SSH Tweaks)
为了解决 VS Code "Setting up SSH Host..." 卡死或超时的问题，做了以下处理：
1.  **创建 `.hushlogin`**: 屏蔽登录欢迎语。
2.  **修改 PAM/SSHD 配置**: 彻底禁用 `pam_motd` 和 `PrintLastLog`。
3.  **禁用 UseDNS**: 加快 SSH 握手速度。

### 多媒体库路径
*   **MPV**: 创建了软链接 `/usr/lib/libmpv.so.1` -> `/usr/lib/x86_64-linux-gnu/libmpv.so`，方便某些依赖库直接调用。
*   **GStreamer**: 标准安装路径，可通过 `gst-inspect-1.0` 验证。

---

## ⚠️ 常见问题 (Troubleshooting)

**Q: 为什么登录后显示的不是 Fish Shell？**
A: 如果你是通过 VS Code 的集成终端连接，可能会受到 VS Code 设置的影响。如果是直接在命令行使用 `ssh root@localhost -p 2222`，应该会自动进入 Fish。如果未进入，输入 `fish` 即可。

**Q: 如何修改 root 密码？**
A:
1.  **构建时修改**: 编辑 Dockerfile 中的 `RUN echo 'root:my_secure_password' | chpasswd` 这一行。
2.  **运行时修改**: 进入容器后运行 `passwd` 命令。

**Q: GStreamer 缺少某个插件？**
A: 当前安装了 `base`, `good`, `bad`, `ugly` 和 `libav`。如果还需要其他特定插件，请修改 Dockerfile 中的 `apt-get install` 部分。

---

## 📋 维护记录 (Changelog)

*   **v1.0**: 初始版本。集成 Ubuntu 22.04, SSH, Fish, UV, GStreamer 全家桶。修复 VS Code 连接稳定性问题。