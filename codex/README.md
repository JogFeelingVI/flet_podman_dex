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

#### jks文件编码
```bash
base64 -i lotter.jks | tr -d '\n'
```

#### debug apk
```bash
adb logcat -v color serious_python:V '*:S'
--------- beginning of main
02-03 09:53:36.833 18799 18836 I serious_python: ERROR handle_Save error: None. LateInitializationError: Field '_instance@394507694' has not been initialized.
02-03 09:53:36.833 18799 18836 I serious_python: Traceback (most recent call last):
02-03 09:53:36.833 18799 18836 I serious_python:   File "/data/user/0/com.flet.lotter/files/flet/app/Customs/filter.py", line 766, in handle_Save
02-03 09:53:36.833 18799 18836 I serious_python:     save_path = await ft.FilePicker().save_file(
02-03 09:53:36.833 18799 18836 I serious_python:                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
02-03 09:53:36.833 18799 18836 I serious_python:   File "/data/user/0/com.flet.lotter/files/flet/python_site_packages/flet/controls/services/file_picker.py", line 241, in save_file
```

#### podman font-family
- ui-sans-serif,system-ui,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji"
- ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace

##### fix
```bash
fc-match monospace
DejaVuSansMono.ttf: "DejaVu Sans Mono" "Book"
```
##### 修复方案
1. ~/.config/fontconfig/conf.d/99-podman-fonts.conf 创建这个文件
2. 文件内容如下

```xml
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
    <!-- 当程序请求 monospace 时，强制优先使用 Source Code Pro -->
    <match target="pattern">
        <test qual="any" name="family"><string>monospace</string></test>
        <edit name="family" mode="prepend" binding="strong">
            <string>Source Code Pro</string>
        </edit>
    </match>
</fontconfig>

```

#### flet load res
- https://gitee.com/jogfeelingvi/lotter_resource/raw/main/fonts/CaveatBrush-Regular.ttf
- https://github.com/JogFeelingVI/lotter_resource/raw/refs/heads/main/fonts/CaveatBrush-Regular.ttf
- https://github.com/JogFeelingVI/lotter_resource/raw/refs/heads/main/fonts/Retro%20Floral.ttf
- https://github.com/JogFeelingVI/lotter_resource/raw/refs/heads/main/fonts.json
- https://gitee.com/jogfeelingvi/lotter_resource/raw/main/fonts.json

