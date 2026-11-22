# @File    : Video.py
# @Time    : 2026/11/17 14:06:55
# @Author  : import flet as ft

import flet as ft
import asyncio
import logging
import flet_video as ftv
from LoveTV.src.storage import load_auth_config

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.Videos")


def build(page: ft.Page, state: dict, navigate) -> ft.View:
    Test_url = "https://event.pull.hebtv.com/live/live101.m3u8"

    async def on_error(e):
        log.info(f"videos play error {e.data}")

    video = ftv.Video(
        expand=True,
        playlist_mode=ftv.PlaylistMode.SINGLE,
        autoplay=False,
        playlist=[ftv.VideoMedia(resource=Test_url)],
        on_error=on_error,
    )

    videos_view = ft.View(
        route="/videos",
        controls=[
            ft.Container(
                expand=True,
                content=video,
            ),
        ],
    )

    async def load_video():
        if "videos" in state:
            video_state: dict = state.get("videos")
            log.info(f"video state {video_state}")

            url = video_state.get("url")

            _, COOKIES = load_auth_config()
            headers = {
                "User-Agent": "AptvPlayer/1.4.10",
                "Referer": url,
                "Cookie": COOKIES,
            }

            video.playlist = [
                ftv.VideoMedia(
                    resource=url,
                    http_headers=headers,
                    extras={"title": "Demo"},
                )
            ]
            if videos_view.page:
                video.update()

    page.run_task(load_video)
    return videos_view
