# @File    : ContinueWatching.py
# @Time    : 2026/11/06 16:52:44
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : 继续观看

import asyncio
import logging

import flet as ft

from LoveTV.src.model.hotmovie import (
    # fetch_bangumi_today,
    fetch_douban_res,
    hotMovie,
    hotTv,
    hotTvShow,
)
from LoveTV.src.model.loadcover import cacha_cover
from LoveTV.src.model.playrecords import (
    load_play_records,
    parse_playrecords,
)
from LoveTV.src.storage import load_auth_config
from LoveTV.src.themes.default import theme

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.SectionList")


class ChildSection(ft.Container):
    """
    剧集海报墙子项组件
    dictraw 不同版本
    v1  {'id': '16803', 'source': 'dyttzy', 'title': '怪诞小镇 第一季', 'source_name': '电影天堂资源', 'year': '2012', 'cover': 'https://img.dytt-tupian.com/upload/vod/20250307-1/77a5dccab7bbab580483288307454f9f.jpg', 'index': 7, 'total_episodes': 20, 'play_time': 455, 'total_time': 1377, 'save_time': 1793942030477, 'search_title': '怪诞小镇 第一季'}
    v2  {'id': '37100984', 'source': 'douban', 'title': '后会友期', 'source_name': None, 'year': '2026', 'cover': 'https://img3.doubanio.com/view/photo/m_ratio_poster/public/p2936933522.jpg', 'index': 0, 'total_episodes': -1, 'playTime': 0, 'totalTime': 0, 'saveTime': None, 'searchTitle': '后会友期', 'doubanId': '37100984', 'rate': '8.7'}
    v2  {'id': '36847425', 'source': 'douban', 'title': '可能的爱', 'source_name': None, 'year': '2026', 'cover': 'https://img3.doubanio.com/view/photo/m_ratio_poster/public/p2935488630.jpg', 'index': 0, 'total_episodes': -1, 'playTime': 0, 'totalTime': 0, 'saveTime': None, 'searchTitle': '可能的爱', 'doubanId': '36847425', 'rate': '8.7'}
    """

    def __init__(self, dictraw, ver=1, /, **kwds):
        self.dictraw = dictraw

        # 提取数据并设置默认值
        self.id = dictraw.get("id")
        self.title = dictraw.get("title", "")
        self.cover = dictraw.get("cover", "")
        self.year = dictraw.get("year", "")
        self.source = dictraw.get("source", "")

        self.dictraw_ver = 1
        if {"douban_id", "rate"}.issubset(dictraw):
            # log.info("dictraw is v2")
            self.dictraw = 2
            self.progress_bar = ft.ProgressBar(visible=False)
            self.source_name_text = ft.Text("No Display", visible=False)
            rate = float(_r) if (_r:=dictraw.get("rate")) else -1.0
            self.right_info = ft.Container(
                content=ft.Text(f"{rate}", size=11 if rate<7 else 13, color=theme.inverse_surface),
                bgcolor=theme.secondary_container if rate <7.0 else theme.inverse_primary,
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                border_radius=4,
                right=6,
                top=6,
                visible=rate > 0,
            )
            # log.info(f"{self.title} rate {rate}")
        else:
            # 这里处理v1的数据结构
            total_eps = dictraw.get("total_episodes")
            play_time = dictraw.get("play_time", 0)
            total_time = dictraw.get("total_time", 1)  # 避免除以 0
            progress_value = min(1.0, max(0.0, play_time / total_time))
            self.progress_bar = ft.ProgressBar(
                value=progress_value,
                color=theme.on_primary_fixed_variant,
                bgcolor=ft.Colors.with_opacity(0.3, theme.surface_container_highest),
                height=3,
                bottom=0,
                left=0,
                right=0,
                visible=progress_value > 0,
            )
            # v1 右上角显示
            self.right_info = ft.Container(
                content=ft.Text(f"共 {total_eps} 集", size=11, color=theme.on_primary),
                bgcolor=theme.primary,
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                # visible=self.episode_info != "None",
                border_radius=4,
                right=6,
                top=6,
                visible=total_eps is not None,
            )
            source_name = dictraw.get("source_name")
            self.source_name_text = ft.Text(
                value=source_name,
                size=12,
                max_lines=1,
                color=theme.on_surface_variant,
                overflow=ft.TextOverflow.ELLIPSIS,
            )

        # 背景色后备方案
        bg_color = ft.Colors.with_opacity(0.75, theme.surface_container)

        self.cover_img_cache = ft.Image(
            src=self.cover,
            fit=ft.BoxFit.COVER,
            width=160,
            height=215,
            border_radius=ft.BorderRadius.only(top_left=10, top_right=10),
        )

        # 定义核心视图组件
        # 1. 顶部海报区域（使用 Stack 层叠封面、年份标签和进度条）
        self.poster_stack = ft.Stack(
            controls=[
                # 海报图片
                self.cover_img_cache,
                # 左上角年份标签 (阴影半透明背景)
                ft.Container(
                    content=ft.Text(
                        self.year,
                        size=11,
                        weight=ft.FontWeight.W_600,
                        color=theme.on_surface,
                    ),
                    bgcolor=ft.Colors.with_opacity(
                        0.75, theme.surface_container_lowest
                    ),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                    border_radius=4,
                    left=6,
                    top=6,
                ),
                # 右上角集数标签
                self.right_info,
                # 底部播放进度条
                self.progress_bar,
            ],
            width=160,
            height=215,
        )

        # 2. 底部标题区域
        self.title_text = ft.Text(
            value=self.title,
            size=14,
            weight=ft.FontWeight.W_700,
            max_lines=1,
            color=theme.on_surface,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        # 整合为垂直布局
        main_layout = ft.Column(
            controls=[
                self.poster_stack,
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self.title_text,
                            self.source_name_text,
                        ],
                        spacing=3,
                    ),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                ),
            ],
            spacing=0,
        )

        # 初始化 Container 属性
        super().__init__(
            content=main_layout,
            width=160,
            bgcolor=bg_color,
            border=ft.Border.all(1, theme.surface_bright),
            border_radius=12,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,  # 裁剪溢出内容以贴合圆角
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),  # 启用过渡动画
            on_hover=self._handle_hover,  # 绑定悬停事件
            **kwds,
        )

    def _handle_hover(self, e):
        """处理鼠标悬停放大、加深边框及变色动效"""
        if e.data:
            # self.scale = 1  # 微微放大
            self.border = ft.Border.all(2, theme.on_secondary_fixed_variant)
            self.title_text.color = theme.primary_container
        else:
            # self.scale = 1.0  # 恢复原状
            self.border = ft.Border.all(1, theme.surface_bright)
            self.title_text.color = theme.on_surface
        self.update()

    def did_mount(self):
        asyncio.create_task(self.loadcover())

    async def loadcover(self):
        img_bytes = await cacha_cover(self.cover, self.source, self.id)
        if img_bytes:
            self.cover_img_cache.src = img_bytes
            self.cover_img_cache.update()


class MainSection(ft.Container):
    def __init__(self, name, types, **kwds):
        self.types = types
        self.title = ft.Row(
            controls=[
                ft.Icon(
                    ft.Icons.MOVIE,
                    size=20,
                    color=theme.primary,
                ),
                ft.Text(name, size=18, weight="bold", color=theme.on_surface),
                ft.VerticalDivider(expand=True),
                ft.Text(
                    "全部播放记录",
                    size=12,
                    weight="bold",
                    color=theme.on_surface_variant,
                ),
                ft.Image(
                    src="images/arrowr.svg", height=12, color=theme.on_surface_variant
                ),
            ],
        )
        self.list = ft.Row(
            controls=[],
            spacing=20,
            alignment=ft.Alignment.TOP_LEFT,
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
        )
        super().__init__(
            padding=ft.Padding(10),
            content=ft.Column(
                controls=[
                    self.title,
                    self.list,
                ],
                spacing=5,
                alignment=ft.Alignment.CENTER,
            ),
            **kwds,
        )

    def did_mount(self):
        asyncio.create_task(self.fetch_server_data(types=self.types))

    # region 数据获取过程
    async def fetch_server_data(self, types: str = "playrecords"):
        """
        args types
        1. playrecords
        2. hotmovie
        3. hottv
        4. hottvshow
        """
        base_url, cookies = load_auth_config()
        match types:
            case "playrecords":
                records = await load_play_records(base_url=base_url, cookies=cookies)
                raw_data = parse_playrecords(records)
            case "hotmovie":
                raw_data = await fetch_douban_res(hotMovie)
                # raw_data = parse_playrecords(raw_data)
                # log.info(f"热门电影 {raw_data[0]}")
            case "hottv":
                raw_data = await fetch_douban_res(hotTv)
                # log.info(f"hottv {raw_data[0]}")
            case "hottvshow":
                raw_data = await fetch_douban_res(hotTvShow)
                # log.info(f"hottv {raw_data[0]}")
            case _:
                raw_data = await fetch_douban_res(hotMovie)
        self.list.controls = [ChildSection(x) for x in raw_data]
        self.list.update()

    # endregion
