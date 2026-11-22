# Dockerfile 优化记录

## 背景

清理 podman 中未使用的 `<none>`（dangling）镜像后，对 `Dockerfile` 进行优化。

## 主要改动

### 1. 移除 `fish`

- apt 安装列表中删除 `fish`。
- 删除 fish 配置相关 `RUN`（`/root/.config/fish`、`fish_add_path`）。
- 删除 bashrc 中自动切换到 fish 的逻辑。
- `/etc/profile.d/uv.sh` 仍保留，保证 uv 在登录 shell（ssh/VS Code）中可见。

### 2. 改变 uv 的安装方式

- 由 `curl` 下载安装脚本改为：

```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
```

- 不再依赖网络下载，构建更可靠；uv 位于 `/usr/local/bin`，已加入 `PATH`。

### 3. 设置 `UV_CACHE_DIR` 并挂载为宿主机/Volume

```dockerfile
ENV UV_CACHE_DIR=/root/.cache/uv
...
VOLUME ["/root/.cache/uv"]
```

- 运行时可挂载宿主机目录或 Docker Volume，复用 uv 缓存：

```bash
podman run -v /path/to/uv-cache:/root/.cache/uv ...
```

### 4. 构建时完全不产生中间层

- 所有 `RUN` 合并为单层（apt、locale、MPV symlink、SSH、profile.d）。
- 使用 BuildKit cache mounts 缓存 apt：

```dockerfile
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    ...
```

- Dockerfile 顶部声明：

```dockerfile
# syntax=docker/dockerfile:1
```

## 构建结果

- 镜像：`localhost/flet-podman-dex:latest`
- ID：`088ae5b0ed5e`
- 大小：837 MB
- 层数明显减少（apt 安装合并为单层，uv 通过 COPY 引入）。

## 备注

- `HEALTHCHECK` 在 OCI 镜像格式下会被忽略；如需生效，构建时使用 `--format docker`。
- 如需最终镜像完全 squash，可构建时加 `--squash`。