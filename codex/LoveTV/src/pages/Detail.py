# @File    : Detail.py
# @Time    : 2026/11/20 07:47:21
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : 影片详细信息页面
import asyncio
import flet as ft
import logging
from LoveTV.src.themes.default import theme
from LoveTV.src.model.configuration import configcol
from LoveTV.src.control.MovieDetailView import SubTitle, CoverStack, MoiveDetailInfo

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.Detail")


def build(page: ft.Page, state: dict, navigate) -> ft.View:
    async def goto(route: str = "/player"):
        if navigate:
            await navigate(route)

    log.info(f"state {state}")

    cardSubtitle = SubTitle("正在加载影片子标题")

    cover = CoverStack()

    moivdetail = MoiveDetailInfo()

    MediaDetail = ft.Container(
        padding=ft.Padding(20, 20, 20, 20),
        bgcolor=theme.surface,
        content=ft.ResponsiveRow(
            controls=[
                cover,
                moivdetail,
            ],
            spacing=8,
            scroll=ft.ScrollMode.HIDDEN,
        ),
    )

    detail_view = ft.View(
        route="/detail",
        scroll=ft.ScrollMode.HIDDEN,
        controls=[
            ft.ResponsiveRow(
                col=configcol(),
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    cardSubtitle,
                    MediaDetail,
                ],
                scroll=ft.ScrollMode.HIDDEN,
            ),
        ],
    )

    async def loadPageData():
        await asyncio.sleep(5)
        dubi = moivdetail.ZoneTitle("4K 杜比")
        moivdetail.ScoreAppend(dubi)

    detail_view.did_mount = lambda: page.run_task(loadPageData)

    return detail_view
