## podman 替换 docker
---

### 第1步：准备文件

在你的项目文件夹中，创建以下两个文件：
参考这个文件:https://www.warp.dev/terminus/ssh-docker-container

**1. `Dockerfile`** (核心文件)

```dockerfile
FROM ubuntu
RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd
RUN echo "root:password" | chpasswd
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
CMD ["/usr/sbin/sshd", "-D"]
```

**2. `id_rsa.pub`** (你的 SSH 公钥)

如果你还没有 SSH 密钥对，请在你的**本地电脑**（不是在 Dockerfile 里）打开终端并运行以下命令来生成一个新的：

```bash
# -t 指定类型, -b 指定强度, -f 指定文件名, -N "" 表示无密码
ssh-keygen -t rsa -b 4096 -f ./id_rsa -N ""
```
这将在当前目录下生成 `id_rsa` (私钥) 和 `id_rsa.pub` (公钥) 两个文件。**我们只需要公钥 `id_rsa.pub`**。

---

### 第2步：构建 Docker 镜像

现在，你的文件夹里应该有 `Dockerfile`, `id_rsa`, `id_rsa.pub` 这几个文件。

打开终端，进入该文件夹，然后运行 `docker build` 命令。我们将通过 `--build-arg` 把公钥内容传递给 Dockerfile。

```bash
docker build \
  --build-arg SSH_USER=devuser \
  --build-arg SSH_PUBLIC_KEY="$(cat id_rsa.pub)" \
  -t python-poetry-ssh .
```
**命令解释：**
*   `--build-arg SSH_USER=devuser`：设置容器内的用户名为 `devuser`。你可以改成你喜欢的名字。
*   `--build-arg SSH_PUBLIC_KEY="$(cat id_rsa.pub)"`：读取 `id_rsa.pub` 文件的内容，并将其作为参数传递给 Dockerfile。
*   `-t python-poetry-ssh`：给这个镜像起一个名字（tag），方便后续使用。
*   `.`：表示 Dockerfile 在当前目录。

---
### 总结与安全提示

*   **为什么不用密码？** 公钥认证远比密码安全，可以防止暴力破解，是服务器管理的标准做法。
*   **不要暴露到公网**：这个 `Dockerfile` 是为**本地开发**设计的。如果你需要将带有 SSH 的容器部署到公网服务器，请务必配置防火墙规则，限制可访问的 IP 地址，以防被攻击。
*   你提到了两次 `poetry`，这可能是个笔误，但请放心，Poetry 已经完美地安装在镜像中了！
*   

### podman build
podman build \
--force-rm \
-t python-uv-ssh .