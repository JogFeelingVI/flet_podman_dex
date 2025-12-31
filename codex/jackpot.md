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