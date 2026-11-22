# @File    : ChildButton.py
# @Time    : 2026/11/05 18:59:13
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : 首页用子级控件

import logging
from dataclasses import dataclass

import flet as ft

from LoveTV.src.themes.default import theme
from LoveTV.src.model.configuration import configcol

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.PapaChild")


@dataclass
class kwitem:
    text: str
    route: str = "/"
    highlight: bool = False


# region 子控件按钮 (建议命名如 NavButton)
class Son_nav(ft.Container):
    def __init__(self, item: kwitem, navigate=None, **kwds):
        self.highlight = item.highlight
        self.route = item.route
        self.navigate = navigate

        # 提取初始颜色，便于复用
        text_color = theme.surface_dim if item.highlight else theme.primary
        bg_color = theme.primary_container if item.highlight else None

        self.text_control = ft.Text(
            item.text,
            color=text_color,
            size=18,
            animate_opacity=200,
        )

        super().__init__(
            height=38,
            border_radius=19,
            content=self.text_control,
            padding=ft.Padding.symmetric(horizontal=7, vertical=5),
            bgcolor=bg_color,
            animate=ft.Animation(duration=200, curve=ft.AnimationCurve.EASE_OUT),
            on_hover=self._handle_hover,
            on_click=self._handle_click,
            **kwds,
        )

    def _handle_hover(self, e):
        # 高亮激活状态下不响应普通 hover 变色
        if self.highlight:
            return
        if e.data:
            self.bgcolor = ft.Colors.with_opacity(1, theme.on_secondary_fixed_variant)
            self.text_control.color = theme.on_surface
        else:
            self.bgcolor = None
            self.text_control.color = theme.primary

        # 必须调用 update 才能刷新状态
        self.update()

    async def _handle_click(self, e):
        if self.navigate:
            await self.navigate(self.route)
            log.info(f"self.navigate(self.route) {self.route}")


# endregion


# region 导航栏 (建议命名如 NavBar) Father, Son
class Father_nav(ft.Container):
    def __init__(self, items: list[kwitem], navigate=None, **kwds):
        """
        :param items: 支持字符串列表 ['Home', 'Settings']
                      或元组列表 [('Home', True), ('Settings', False)]
        """
        self.navigate = navigate
        self.buttons = [self._create_child(item) for item in items]

        super().__init__(
            content=ft.Row(
                controls=self.buttons,
                # spacing=5,  # 按钮之间的间距
                tight=True,  # 紧凑包裹
            ),
            height=48,
            padding=5,
            border_radius=24,
            # bgcolor=ft.Colors.with_opacity(0.30, theme.surface_bright),
            **kwds,
        )

    def _create_child(self, item: kwitem) -> Son_nav:
        # 支持传入纯字符串或带高亮参数的元组
        return Son_nav(item, self.navigate)


# endregion
