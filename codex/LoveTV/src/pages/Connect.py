# @File    : Connect.py
# @Time    : 2026/11/12 07:43:42
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : 请在此处输入文件描述

import logging
import asyncio

import flet as ft
import flet_lottie as ftlo

from LoveTV.src.themes.default import theme
from LoveTV.src.storage import load_auth_config
from LoveTV.src.model.connectserver import (
    detail_screen_flow,
    ProgressBus,
    configureClient,
    build_player_launch,
    build_play_url,
    _source_key,
)

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.Connect")


def build(page: ft.Page, state: dict, navigate) -> ft.View:

    async def open_player():
        await navigate("/player")

    col_conf = {"xs": 12, "sm": 6, "md": 6, "lg": 6, "xl": 6, "xxl": 6}

    indicator = ft.Container(
        col=0,
        height=16,
        width=0,
        border_radius=8,
        gradient=ft.LinearGradient(
            colors=[theme.primary_container, theme.secondary],
            begin=ft.Alignment.CENTER_LEFT,
            end=ft.Alignment.CENTER_RIGHT,
        ),
    )

    indicator_shell = ft.Container(
        col=col_conf,
        height=18,
        border_radius=9,
        padding=0,
        bgcolor=theme.surface_bright,
        content=ft.KeyboardListener(
            autofocus=True,
            content=ft.ResponsiveRow(
                columns=100,
                controls=[indicator],
            ),
        ),
    )

    InfoList = ft.Column(
        spacing=3,
        controls=[ft.Text("正在加载程序资源...", size=14, color=theme.primary)],
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    Information = ft.Container(
        col=col_conf,
        margin=10,
        padding=10,
        border_radius=10,
        max_height=200,
        bgcolor=theme.surface_container_lowest,
        content=InfoList,
        border=ft.Border.all(1, theme.inverse_on_surface),
    )

    async def on_progress(pct, task):
        # nonlocal progrpcess
        if InfoList.controls.__len__() > 6:
            InfoList.controls.pop(0)
        for item in InfoList.controls:
            item.color = None
        InfoList.controls.append(ft.Text(task, size=14, color=theme.primary))
        baifengbi.value = f"{pct}%"
        indicator.col = pct
        InfoList.update()
        indicator.update()
        baifengbi.update()

    async def update_flow():
        entry = state.get("connect", None)
        if entry:
            server, cookie = load_auth_config()
            log.info(f"server {server}")
            configureClient(server, cookie, entry["source"])
            bus = ProgressBus()
            bus.on(on_progress)
            restate = await detail_screen_flow(entry=entry, bus=bus)
            launch = build_player_launch(entry, restate, 0)
            src = next(
                s
                for s in launch["sources"]
                if _source_key(s) == launch["selectedSourceKey"]
            )
            ep_index = launch["episodeIndex"]
            raw_url = src["episodes"][ep_index]
            url = build_play_url(raw_url)
            start_sec = launch["startPositionMs"] // 1000
            state["videos"] = {
                "url": url,
                "start_sec": start_sec,
                "title": entry["title"],
            }
            await asyncio.sleep(3)
            if "connect" in state:
                del state["connect"]
            await navigate("/videos")
        else:
            await on_progress(1, "无法获取 entry 参数")
            await navigate("/player")

        # log.info(f"re state {restate}")
        # rven = {
        #     "rawResults": [
        #         {
        #             "source": "ffzy",
        #             "id": "10991",
        #             "title": "怪诞小镇 第一季",
        #             "year": "2012",
        #             "episodes": [1, 2, 3],
        #         }
        #     ],
        #     "sourcesComplete": True,
        #     "detailsLoading": False,
        #     "details": None,
        #     "detailsError": None,
        #     "bangumiDetails": None,
        #     "tmdbTrigger": None,
        #     "tmdbArt": None,
        #     "tmdbRef": None,
        #     "tier2Target": None,
        #     "playRecords": {},
        #     "favoriteKeys": set(),
        #     "sources": [
        #         {
        #             "source": "ffzy",
        #             "id": "10991",
        #             "title": "怪诞小镇 第一季",
        #             "year": "2012",
        #             "episodes": [1, 2, 3],
        #         }
        #     ],
        #     "selectedSourceKey": "ffzy+10991",
        # }

    connect_view = ft.View(
        route="/connect",
        controls=[
            ft.ResponsiveRow(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        col=col_conf,
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ftlo.Lottie(
                                    src="lotties/connect.json",
                                    animate=True,
                                    width=210,
                                    height=210,
                                    filter_quality=ft.FilterQuality.HIGH,
                                ),
                                ft.Text(
                                    "正在建立视频安全连接...",
                                    size=25,
                                    weight="bold",
                                    color=theme.on_surface,
                                ),
                                ft.Text(
                                    "检测视频源,择优选择视频源,实时获取视频切片",
                                    size=16,
                                    color=theme.surface_tint,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            "💕 影片预载中...",
                                            size=14,
                                            color=theme.primary,
                                        ),
                                        baifengbi := ft.Text(
                                            "--",
                                            size=14,
                                            color=theme.primary,
                                            weight="bold",
                                        ),
                                    ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                indicator_shell,
                                Information,
                            ],
                        ),
                    ),
                ],
            ),
        ],
    )
    # connect_view.on_size_change =
    page.run_task(update_flow)
    return connect_view
