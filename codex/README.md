## codex
#### *flet 环境 0.80*
---
> 使用 uv 更新 Python 项目依赖可以通过更新配置文件并同步环境来实现。核心命令是 uv sync (更新所有依赖) 和 uv add @latest(更新特定包)。对于使用pyproject.toml 的项目，uv` 会自动更新 lock 文件。 

### 常用更新命令
#### 更新所有依赖到最新版本 (根据 pyproject.toml 或 requirements.txt):
```bash
uv sync
```
*此命令会重新计算依赖并更新 uv.lock 文件。*
#### 将特定依赖升级到最新版本:
```bash
uv add <package_name>@latest
```
*例如：uv add requests@latest，这会自动修改 pyproject.toml 并更新锁文件。*

#### 将所有依赖升级到最新版本并更新 pyproject.toml:
```bash
uv lock --upgrade
uv sync
```
#### 同步开发环境依赖:
```bash
uv sync --dev
```
--- 
### 基于 requirements.in 的工作流
> 如果项目使用 requirements.in 管理依赖：
> 升级包: 编辑 requirements.in 修改版本号或直接使用 uv pip compile 升级。
#### 重新编译锁定文件:
```bash
uv pip compile requirements.in -o requirements.txt
```
#### 同步到环境:
```bash
uv pip sync requirements.txt
```