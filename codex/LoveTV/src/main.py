# @Author: JogFeelingVI
# @Date:   2026-11-02 23:47:07
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-11-03 05:40:44
import logging

import flet as ft

from LoveTV.src.pages import Author, Login, Player
from LoveTV.src.storage import login_state
from LoveTV.src.themes.default import theme

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.main")


async def main(page: ft.Page):
    page.title = "LoveTV"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = theme.surface
    page.padding = 20
    page.expand = True

    state = {"login_mode": False, "user": ""}

    builders = {
        "/": Player.build,
        "/login": Login.build,
        "/player": Player.build,
        "/author": Author.build,
        "/connect": Author.build,
    }

    state.update(login_state())

    log.info(f"state {state}")

    async def navigate(route: str):
        await page.push_route(route)

    def render_route(e=None):
        log.info(f"rule is {e}")
        page.views.clear()

        # 根页面作为返回栈的起点
        page.views.append(builders[e](page, state, navigate))

        # 当前子页面显示在栈顶
        if page.route != "/":
            builder = builders.get(page.route, Author.build)
            page.views.append(builder(page, state, navigate))

        page.update()

    def on_route_change(e: ft.RouteChangeEvent):
        # push_route() 改变路由后会触发这里
        render_route(e.route)

    async def on_view_pop(e: ft.ViewPopEvent):
        # 系统返回键/手势触发。移除当前页，再返回上一页
        if e.view is None or len(page.views) <= 1:
            return

        page.views.remove(e.view)
        previous_view = page.views[-1]
        await page.push_route(previous_view.route)

    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop

    if state["login_mode"] and state["user"] != "":
        render_route("/player")
    else:
        render_route("/login")


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
