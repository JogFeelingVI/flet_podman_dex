## 使用flet开发一块手机应用，界面布局如下
1. 顶部是appbar 第一个显示程序图标，第二个显示程序名称“jackpot”,第三显示三个折叠菜单
    1. 菜单显示 `send`, `compo`, `quit`
    
2. 中间是不同的页面显示区域
3. 最下面是三个页面的切换按钮，使用NavigationBar来做。
    1. `seting` 页面，说明信息，包含三个RangeSlide
    2. `fillter` 页面，说明信息，添加各种过滤条件
    3. `data` 页面，说明信息，显示筛选之后的数据
    4. 要求有页面切换功能。

---
## gameini apk
这是一个使用 Flet 开发的符合你要求的手机应用原型。它包含了响应式的 `AppBar`、带菜单的操作栏、页面切换逻辑以及底部 `NavigationBar`。

### 核心代码实现

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Jackpot App"
    page.theme_mode = ft.ThemeMode.LIGHT
    # 设置移动端适配的内边距
    page.padding = 0
    
    # --- 页面逻辑控制 ---
    def on_navigation_change(e):
        index = e.control.selected_index
        # 切换中间的内容区域
        if index == 0:
            content_area.content = setting_view
        elif index == 1:
            content_area.content = filter_view
        elif index == 2:
            content_area.content = data_view
        page.update()

    def handle_menu_click(e):
        print(f"Menu clicked: {e.control.data}")
        if e.control.data == "quit":
            page.window_close()

    # --- 1. 各个页面的 UI 定义 ---

    # Setting 页面
    setting_view = ft.Column(
        controls=[
            ft.Text("设置页面", size=25, weight=ft.FontWeight.BOLD),
            ft.Text("请调节参数范围："),
            ft.Text("参数 A 范围"),
            ft.RangeSlider(min=0, max=100, start_value=20, end_value=80, label_format="{value}"),
            ft.Text("参数 B 范围"),
            ft.RangeSlider(min=0, max=100, start_value=10, end_value=50, label_format="{value}"),
            ft.Text("参数 C 范围"),
            ft.RangeSlider(min=0, max=100, start_value=40, end_value=90, label_format="{value}"),
        ],
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
        alignment=ft.MainAxisAlignment.START,
    )

    # Filter 页面
    filter_view = ft.Column(
        controls=[
            ft.Text("过滤页面", size=25, weight=ft.FontWeight.BOLD),
            ft.Text("在此添加各种过滤条件："),
            ft.TextField(label="关键词过滤", prefix_icon=ft.icons.FILTER_ALT),
            ft.Dropdown(
                label="分类筛选",
                options=[
                    ft.dropdown.Option("选项 1"),
                    ft.dropdown.Option("选项 2"),
                ],
            ),
            ft.Checkbox(label="仅显示有效数据"),
        ],
        expand=True,
    )

    # Data 页面
    data_view = ft.Column(
        controls=[
            ft.Text("数据页面", size=25, weight=ft.FontWeight.BOLD),
            ft.Text("显示筛选后的结果："),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("结果")),
                ],
                rows=[
                    ft.DataRow(cells=[ft.DataCell(ft.Text("1")), ft.DataCell(ft.Text("数据 A"))]),
                    ft.DataRow(cells=[ft.DataCell(ft.Text("2")), ft.DataCell(ft.Text("数据 B"))]),
                ],
            ),
        ],
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
    )

    # --- 2. 界面组件定义 ---

    # 中间显示区域容器
    content_area = ft.Container(
        content=setting_view, # 默认显示设置页
        expand=True,
        padding=20,
    )

    # 顶部 AppBar
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.MONEY_OFF_CSRED_ROUNDED, color=ft.colors.AMBER), # 程序图标
        leading_width=40,
        title=ft.Text("jackpot", weight=ft.FontWeight.BOLD),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="Send", icon=ft.icons.SEND, data="send", on_click=handle_menu_click),
                    ft.PopupMenuItem(text="Compo", icon=ft.icons.IMAGE_OUTLINED, data="compo", on_click=handle_menu_click),
                    ft.PopupMenuItem(text="Quit", icon=ft.icons.EXIT_TO_APP, data="quit", on_click=handle_menu_click),
                ]
            ),
        ],
    )

    # 底部 NavigationBar
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.SETTINGS_OUTLINED, selected_icon=ft.icons.SETTINGS, label="Setting"),
            ft.NavigationDestination(icon=ft.icons.FILTER_LIST_ALT, label="Filter"),
            ft.NavigationDestination(icon=ft.icons.DATA_EXPLORATION_OUTLINED, label="Data"),
        ],
        on_change=on_navigation_change,
    )

    # 将内容添加到页面
    page.add(content_area)

# 运行应用
ft.app(target=main)
```

### 代码要点说明：

1.  **AppBar (顶部栏)**:
    *   `leading`: 设置了程序图标。
    *   `title`: 设置为 "jackpot"。
    *   `actions`: 使用 `ft.PopupMenuButton` 实现了折叠菜单，包含 `send`, `compo`, `quit` 三个选项，并绑定了点击事件。

2.  **页面切换逻辑**:
    *   定义了一个 `content_area` (一个 `ft.Container`) 作为占位符。
    *   在 `NavigationBar` 的 `on_change` 事件中，根据选中的索引（0, 1, 2）动态修改 `content_area.content` 的内容。

3.  **RangeSlider (设置页)**:
    *   在 `setting_view` 中使用了三个 `ft.RangeSlider`。你可以通过 `start_value` 和 `end_value` 获取用户选择的范围。

4.  **布局优化**:
    *   每个页面视图（`setting_view`, `filter_view`, `data_view`）都使用了 `ft.Column` 组织，并设置了 `expand=True` 确保填满中间区域。
    *   使用了 `scroll=ft.ScrollMode.ADAPTIVE` 确保当内容超过手机屏幕高度时可以滑动。

5.  **手机适配**:
    *   设置 `page.padding = 0` 确保背景色和导航栏能紧贴边缘。
    *   `ft.NavigationBar` 是 Material Design 3 标准的底部导航控件，非常适合手机端。

### 如何运行：
1. 安装 flet：`pip install flet`
2. 保存上述代码为 `app.py`。
3. 运行：`python app.py`（在电脑上会弹出一个窗口模拟手机效果）。
4. 如果要发布到手机，可以使用 `flet build apk` (安卓) 或 `flet build ios` (iOS)。

### Android Error
```bash
12-31 20:09:44.627 21184 21222 I serious_python:   File "/data/user/0/com.flet.buildflet/files/flet/app/main.py", line 191, in main
12-31 20:09:44.627 21184 21222 I serious_python:     selectPx = read_from_json()
12-31 20:09:44.627 21184 21222 I serious_python:                ^^^^^^^^^^^^^^^^
12-31 20:09:44.627 21184 21222 I serious_python:   File "/data/user/0/com.flet.buildflet/files/flet/app/main.py", line 176, in read_from_json
12-31 20:09:44.627 21184 21222 I serious_python:     with open(jackpot_settings_path, "r") as f:
12-31 20:09:44.627 21184 21222 I serious_python:          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
12-31 20:09:44.627 21184 21222 I serious_python: FileNotFoundError: [Errno 2] No such file or directory: '/data/user/0/com.flet.buildflet/app_flutter/jackpot_settings.json'
```

### fix dockder
在 Docker + SSH + VSCode 转发这种链路下，Flet 运行慢通常不是因为代码逻辑，而是因为 **“文件监控压力”、“网络隧道延迟”** 以及 **“Web 资源重复加载”** 导致的。

你可以通过以下几个针对性的优化，显著提升热重载（Hot Reload）的速度：

### 1. 优化 Flet 监听范围（最有效）
Flet 在热重载时会扫描项目目录。如果你的 Docker 容器里有大量的冗余文件（如 `.venv` 虚拟环境、`__pycache__` 或大量数据文件），Flet 扫描它们会消耗大量 CPU，导致保存后延迟几秒才刷新。

**解决方法：** 使用 `--ignore` 参数排除无关文件夹。
```bash
# 假设你的虚拟环境叫 .venv，且有很多缓存
flet run --web --port 8550 --ignore ".venv, __pycache__, build, storage" app.py
```

### 2. 解决 VSCode 端口转发的延迟
VSCode 的 `Ports` 转发是通过 SSH 隧道实现的，有时其内部的“自动检测”机制会导致数据传输卡顿。

**解决方法：** 
*   在 VSCode 端口面板中，右键点击 `8550` 端口，将 **"Port Forwarding Protocol" (转发协议)** 从 `Auto` 改为 **`HTTPS`** (如果是 https) 或 **`HTTP`** (通常设为 HTTP)。
*   如果你在局域网内，**不要用 VSCode 转发**，直接在浏览器访问 `http://服务器IP:8550`。这会绕过 SSH 加密隧道，速度极快（前提是 Docker 启动时用了 `-p 8550:8550`）。

### 3. 禁止 Python 生成字节码文件
Docker 容器在写入 `__pycache__` 时，如果磁盘映射（Volume）性能一般，会拖慢进程重载速度。

**解决方法：** 环境变量设置不生成缓存。
```bash
export PYTHONDONTWRITEBYTECODE=1
flet run --web --port 8550 app.py
```

### 4. 减少 Web 端资源加载
Flet Web 模式在每次热重载时，浏览器可能会尝试重新下载一些 JS 资源。

**解决方法：** 
*   **保持浏览器标签页不关闭**：Flet 的热重载是局部更新或自动重刷，不要手动频繁按 F5。
*   **检查 CPU 占用**：在 Docker 里运行 `top`。如果 `python` 进程在保存代码后 CPU 瞬间飙到 100% 且持续很久，说明你的 `flet run` 正在扫描太多的文件（回到第 1 点解决）。

---
## filter
### 现在的布局如下
```python
# Filter 页面
    filter_view = ft.Column(
        controls=[
            ft.Text("Filter", size=25, weight=ft.FontWeight.BOLD),
            ft.Text("Add various filtering criteria here:"),
            ft.TextField(label="关键词过滤", prefix_icon=ft.Icons.FILTER_2_SHARP),
            ft.Dropdown(
                label="分类筛选",
                options=[
                    ft.dropdown.Option("选项 1"),
                    ft.dropdown.Option("选项 2"),
                ],
            ),
            ft.Checkbox(label="仅显示有效数据"),
        ],
        expand=True,
    )
```
### 改变目的
- t.TextField(label="关键词过滤" 一下的内容都不需要，
- 添加一个按钮`add filter`
- 弹出一个对话框,标题是`Filter Settings`
- 体一行是 `：Target` 是一个下来列表，显示在”setings“页面启用的选项
- 第二行 `Conditions`，是一个可以自动填充的文本输入框。
- 第三行 显示`Apply`, `Cancel` 两个按钮
- apply用红色背景，白色字体
- Cancel 用主题默认颜色就可以，

## 当用户点击apply后，对话框消失，在页面中的列表中显示`Conditions`输入的内容，使用ListTile来显示
- `ListTile` 向右滑动删除，长安返回`Filter Settings`对话框编辑，
