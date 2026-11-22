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
from LoveTV.src.model.configuration import configcol

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
    lishibut = IconTextButton("历史", navigate=navigate, route="/author")
    shoucangbut = IconTextButton("收藏", ft.Icons.FAVORITE)
    huiyuanbut = IconTextButton(
        "会员", ft.Icons.DIAMOND, navigate=navigate, route="/login"
    )
    row = ft.Row(
        # vertical_alignment=ft.CrossAxisAlignment.START,
        alignment=ft.MainAxisAlignment.START,
        spacing=5,
        wrap=True,
        controls=[
            ft.Image(src="images/smlogo.svg", height=48),
            nvabutton,
            serchinput,
            lishibut,
            shoucangbut,
            huiyuanbut,
        ],
    )
    return row


def build(page: ft.Page, state: dict, navigate) -> ft.View:
    async def open_login():
        await navigate("/login")

    navbar = navigation(navigate)
    playrecord = MainSection("继续观看", "playrecords", navigate, state)
    hotmovie = MainSection("Hot Movie", "hotmovie", navigate, state)
    hottv = MainSection("热门剧集", "hottv", navigate, state)
    hottvshow = MainSection("综艺大观", "hottvshow", navigate, state)

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

    async def loadpage():
        if state["login_mode"] != True or state["user"] == "":
            await navigate("/login")
            return 0

    player_view.did_mount = lambda: page.run_task(loadpage)

    return player_view
