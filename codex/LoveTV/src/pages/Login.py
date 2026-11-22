# @Author: JogFeelingVI
# @Date:   2026-11-03 00:14:22
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-11-03 23:14:56
# @File    : Login.py
# @Time    : 2026/11/03 08:16:11
# @Author  : JogFeelingVI
# @Email   : glifelse@gmail.com
# @Desc    : 用户登录界面
import flet as ft

from LoveTV.src.control.FormInputField import FormInputField
from LoveTV.src.model.login import logintointerface
from LoveTV.src.storage import save_login
from LoveTV.src.themes.default import theme
from LoveTV.src.model.configuration import configcol


def build(page: ft.Page, state: dict, navigate) -> ft.View:
    async def open_player():
        await navigate("/player")

    if state["login_mode"] and state["user"] != "":
        page.run_task(open_player)

    # region gradient_button_hover
    def gradient_button_hover(e):
        if e.data:
            gradient_button.shadow = ft.BoxShadow(
                color=ft.Colors.with_opacity(0.85, theme.on_secondary_container),
                blur_radius=10,
                spread_radius=2,
            )
        else:
            gradient_button.shadow = ft.BoxShadow(
                color=ft.Colors.with_opacity(0.45, theme.primary),
                blur_radius=10,
                spread_radius=2,
            )
        gradient_button.update()

    # endregion

    # region gradient_button_click
    async def gradient_button_click(e):
        # 1. 获取并清理输入数据
        interface = interface_input.text_field.value.strip()
        username = username_input.text_field.value.strip()
        password = password_input.text_field.value.strip()

        # 2. 基础输入校验，避免不必要的网络请求
        if not username or not password:
            lock_icon.icon = ft.Icons.LINK_OFF
            lock_text.value = "请填写所有必填项"
            e.page.update()  # 统一页面更新
            return

        try:
            # 3. 执行登录（由于外层是 async，如果 logintointerface 支持异步请加 await）
            recode = logintointerface(interface, username, password)

            # 4. 统一处理登录成功逻辑
            if recode and recode.get("response_code") == 200:
                recode["username"] = username
                state["login_mode"] = (True,)
                state["user"] = username
                save_login(recode)
                await open_player()

        except (OSError, ValueError) as ex:
            # 捕获潜在的网络异常或代码报错
            print(f"登录出现错误 {ex}")

        # 5. 合并去重后的登录失败逻辑
        lock_icon.icon = ft.Icons.LINK_OFF
        lock_text.value = "用户名或密码错误"

        # 使用 e.page.update() 或父容器 update，比单个组件分别 update 效率更高，防止界面闪烁
        e.page.update()

    # endregion

    lock_icon = ft.Icon(ft.Icons.LOCK, color=theme.on_surface)
    lock_text = ft.Text(
        "Login To LoveTV", color=theme.on_surface, weight=ft.FontWeight.BOLD
    )
    login_view = ft.View(
        route="/login",
        padding=20,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.HIDDEN,
        controls=[
            ft.ResponsiveRow(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        col=configcol(xs=12, sm=6),
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Image(
                                src="images/icon.svg",
                                width=168,
                                height=168,
                                filter_quality=ft.FilterQuality.HIGH,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        "LoveTV",
                                        size=30,
                                        weight=ft.FontWeight.BOLD,
                                        color=theme.on_surface,
                                    ),
                                    ft.Image(src="images/adm.svg", height=18),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                spacing=5,
                            ),
                            ft.Text(
                                "❤️遇见心动,点亮一刻温情",
                                size=16,
                                color=theme.on_surface_variant,
                            ),
                            interface_input := FormInputField(
                                label="Interface:",
                                hint="http://127.0.0.1:3000",
                            ),
                            username_input := FormInputField(
                                label="Username:",
                                hint="Enter your username",
                            ),
                            password_input := FormInputField(
                                label="Password:",
                                password=True,
                                can_reveal_password=True,
                            ),
                            gradient_button := ft.Container(
                                width=300,
                                height=50,
                                padding=15,
                                border_radius=25,
                                gradient=ft.LinearGradient(
                                    colors=[
                                        theme.primary_container,
                                        theme.secondary_container,
                                    ],
                                    begin=ft.Alignment.CENTER_LEFT,
                                    end=ft.Alignment.CENTER_RIGHT,
                                ),
                                shadow=ft.BoxShadow(
                                    color=ft.Colors.with_opacity(0.45, theme.primary),
                                    blur_radius=10,
                                    spread_radius=2,
                                ),
                                content=ft.Row(
                                    controls=[
                                        lock_icon,
                                        lock_text,
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                on_hover=gradient_button_hover,
                                on_click=gradient_button_click,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
    return login_view
