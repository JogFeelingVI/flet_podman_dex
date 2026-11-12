# @Author: JogFeelingVI
# @Date:   2026-11-03 00:14:43
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-11-03 01:48:01
# @File    : Player.py
# @Time    : 2026/11/03 08:46:03
# @Author  : JogFeelingVI
# @Email   : glifelse@gmail.com
# @Desc    : 看电视的界面

import logging

import flet as ft

from LoveTV.src.control.FatherSon import Father_nav, kwitem
from LoveTV.src.control.IconTextButton import IconTextButton
from LoveTV.src.control.SearchInput import SearchInput
from LoveTV.src.control.SectionList import MainSection
from LoveTV.src.themes.default import theme

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.Player")


def navigation(navigate) -> ft.Control:
    """显示导航栏"""
    nav_items = [
        kwitem("首页", "/author", True),
        kwitem("电影", "/", False),
        kwitem("剧集", "/", False),
        kwitem("综艺", "/", False),
        kwitem("动漫", "/", False),
        kwitem("直播", "/", False),
    ]
    nvabutton = Father_nav(nav_items, navigate=navigate)
    serchinput = SearchInput()
    lishi_but = IconTextButton("历史", navigate=navigate, route="/author")
    shoucang_but = IconTextButton("收藏", ft.Icons.FAVORITE)
    huiyuan_but = IconTextButton("会员", ft.Icons.DIAMOND)
    row = ft.Container(
        padding=10,
        border_radius=15,
        bgcolor=theme.surface_dim,
        content=ft.Row(
            controls=[
                ft.Image(src="images/smlogo.svg", height=48),
                ft.VerticalDivider(width=20),
                nvabutton,
                ft.VerticalDivider(width=15),
                serchinput,
                ft.VerticalDivider(expand=True),
                lishi_but,
                shoucang_but,
                huiyuan_but,
            ],
            expand=True,
        ),
        shadow=ft.BoxShadow(
            color=ft.Colors.with_opacity(0.20, theme.primary),
            blur_radius=2,
            spread_radius=1,
        ),
        clip_behavior=ft.ClipBehavior.NONE,
    )
    return row


def build(page: ft.Page, state: dict, navigate) -> ft.View:
    async def open_login():
        await navigate("/login")

    async def _handle_open_login(e):
        await open_login()

    navbar = navigation(navigate)
    playrecord = MainSection("继续观看", "playrecords")
    hotmovie = MainSection("Hot Movie", "hotmovie")
    hottv = MainSection("热门剧集", "hottv")
    hottvshow = MainSection("综艺大观", "hottvshow")

    player_view = ft.View(
        route="/player",
        controls=[
            ft.Column(
                controls=[
                    navbar,
                    playrecord,
                    hotmovie,
                    hottv,
                    hottvshow,
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
        ],
        scroll=ft.ScrollMode.HIDDEN,
    )
    log.info(f"state is {state}")
    return player_view
