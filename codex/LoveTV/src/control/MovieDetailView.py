# @File    : MovieDetailView.py
# @Time    : 2026/11/20 23:02:36
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : 详细页用到的控件封装

import textwrap
import flet as ft
import logging
from LoveTV.src.themes.default import theme
from LoveTV.src.model.configuration import configcol

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.MovieDetailView")


# region 影片子标题
class SubTitle(ft.Container):
    def __init__(self, text: str = "", **kwds):
        self._mount = False
        self.text = ft.Text(text, size=18, color=theme.primary)
        super().__init__(
            padding=ft.Padding(20, 8, 8, 8),
            content=self.text,
            border=ft.Border(bottom=ft.BorderSide(2, theme.on_secondary)),
            **kwds,
        )

    def update_text(self, text: str):
        if text:
            self.text.value = text
            if self._mount:
                self.text.update()

    def did_mount(self):
        self._mount = True
        return super().did_mount()

    def will_unmount(self):
        self._mount = False
        return super().will_unmount()


# endregion


# region 影片封面
class CoverStack(ft.Stack):
    def __init__(
        self,
        cover: str = None,
        year: str | int = None,
        title: str = None,
        total: int = None,
        **kwds,
    ):
        cover = cover if cover else "images/cover.png"
        year = year if year else "1949"
        title = title if title else "正在获取"
        total = total if total else "正在获取"

        self._mount = False

        self.cover_img = ft.Image(
            src=cover,
            fit=ft.BoxFit.COVER,
            border_radius=ft.BorderRadius.only(top_left=10, top_right=10),
        )

        self.year = ft.Container(
            padding=ft.Padding.symmetric(vertical=5, horizontal=15),
            bgcolor=theme.tertiary_container,
            content=ft.Text(year, size=18),
            border_radius=10,
            top=8,
            left=8,
        )

        self.title = ft.Container(
            padding=ft.Padding.symmetric(vertical=5, horizontal=15),
            bgcolor=ft.Colors.with_opacity(0.65, theme.primary_container),
            content=ft.Text(title, size=20),
            border_radius=10,
            bottom=8,
            left=8,
        )

        self.total = ft.Container(
            padding=ft.Padding.symmetric(vertical=5, horizontal=15),
            bgcolor=theme.secondary_container,
            content=ft.Text(total, size=19),
            border_radius=10,
            top=8,
            right=8,
        )

        super().__init__(
            col=configcol(xs=12, sm=3),
            aspect_ratio=27 / 40,
            fit=ft.StackFit.EXPAND,
            controls=[self.cover_img, self.year, self.title, self.total],
            **kwds,
        )

    def did_mount(self):
        self._mount = True
        return super().did_mount()

    def will_unmount(self):
        self._mount = False
        return super().will_unmount()

    def update_cover(self, cover: str | None):
        """安全更新封面图"""
        if cover and cover != self.cover_img.src:
            self.cover_img.src = cover
            if self._mount:
                self.cover_img.update()

    def update_year(self, year: str | int = None):
        if year and isinstance(year, str) and isinstance(year, int):
            self.year.content.value = f"{year}"
            if self._mount:
                self.year.update()

    def update_title(self, title: str = None):
        if title and isinstance(title, str()):
            self.title.content.value = title
            if self._mount:
                self.title.update()

    def update_total(self, total: str = None):
        if total and isinstance(total, str()):
            self.total.content.value = total
            if self._mount:
                self.total.update()


# endregion


# region IconButton
class IconButton(ft.Container):
    def __init__(
        self,
        height: int = 60,
        icon: ft.IconData = None,
        text: str = None,
        plan: str = "a",
        **kwds,
    ):
        icon = icon if icon else ft.Icons.FAVORITE
        plan = plan if plan in "ab" else "a"
        _rowline = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        )
        _rowctls = []
        _rowctls.append(ft.Icon(icon=ft.Icons.PLAY_ARROW, size=18, color=theme.surface))
        if text:
            _rowctls.append(
                ft.Text("立即播放第1集", size=18, color=theme.surface, weight="bold"),
            )
        shadow_plan = {
            "a": ft.BoxShadow(6, 13, theme.on_primary),
            "b": ft.BoxShadow(
                6, 13, ft.Colors.with_opacity(0.6, theme.surface_container_highest)
            ),
        }

        kwds.setdefault("height", height)
        kwds.setdefault("border_radius", int(height / 2))
        kwds.setdefault("padding", ft.Padding.symmetric(horizontal=24))
        kwds.setdefault("shadow", shadow_plan["a"])
        kwds.setdefault("content", _rowline)
        super().__init__(**kwds)


"""self.playnow = ft.Container(
    height=60,
    border_radius=30,
    bgcolor=theme.primary_container,
    padding=ft.Padding.symmetric(horizontal=24),
    content=ft.Row(
        controls=[
            ft.Icon(icon=ft.Icons.PLAY_ARROW, size=18, color=theme.surface),
            ft.Text(
                "立即播放第1集", size=18, color=theme.surface, weight="bold"
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        tight=True,
    ),
    shadow=ft.BoxShadow(6, 13, theme.on_primary),
)"""
# endregion


# region 影片详细信息
class MoiveDetailInfo(ft.Container):
    def __init__(
        self, bigtitle: str = None, subtitle: str = None, score: str = None, **kwds
    ):
        bigtitle = bigtitle if bigtitle else "正在获取"
        subtitle = subtitle if subtitle else "正在获取"
        score = f"★ {score}" if score else "★ 10"
        self._mount = False
        self.bigTitle = ft.Text(bigtitle, size=36, color=theme.inverse_surface)
        self.subTitle = ft.Text(subtitle, size=20, color=theme.on_surface_variant)
        self.score = ft.Row(
            controls=[
                self.ZoneTitle(score),
                self.ZoneTitle("2024 / 美国", color=theme.on_surface_variant),
                self.ZoneTitle("动作 / 战争 / 军事 / 剧情"),
            ],
            wrap=True,
        )

        self.markdown = ft.Markdown(
            value=textwrap.dedent("""
            - `简体中文`
                > 看电影不仅是忙碌生活中的一种放松方式，更是一场丰富心灵的旅程。通过大银幕，
                我们可以在短短两小时内体验不同的人生，走进从未去过的世界，从而拓宽视野并加深对人性的理解。
                优秀的电影往往能引发深刻的情感共鸣，帮助我们释放压力、疗愈情绪。
                此外，与家人或朋友一起观影，还能创造共同的话题，拉近彼此的距离。
                总而言之，看电影既能愉悦身心，又能滋养精神，是提升生活品质的绝佳选择。

            - `English`
                > Watching movies is not only a way to unwind from our busy lives, 
                but also a journey that enriches the soul. Through the big screen, 
                we can experience different lives and step into worlds we have never visited in just two hours, 
                thereby broadening our horizons and deepening our understanding of human nature. 
                Great films often strike a deep emotional chord, helping us relieve stress and heal our emotions. 
                Moreover, watching movies with family or friends creates shared topics of conversation 
                and brings us closer together. In short, watching movies both delights the body and mind 
                and nourishes the spirit, making it a wonderful way to enhance our quality of life."""),
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            soft_line_break=False,
            md_style_sheet=ft.MarkdownStyleSheet(
                p_text_style=ft.TextStyle(size=15),  # 普通段落及列表字号
                blockquote_text_style=ft.TextStyle(
                    size=18,
                    color=ft.Colors.with_opacity(0.75, theme.on_surface),
                ),  # > 引用文字字号
                # 让引用块（>）的背景也完全透明
                blockquote_decoration=ft.BoxDecoration(
                    bgcolor=ft.Colors.TRANSPARENT,
                ),
            ),
            expand=True,
        )

        self.playnow = ft.Container(
            height=60,
            border_radius=30,
            bgcolor=theme.primary_container,
            padding=ft.Padding.symmetric(horizontal=24),
            content=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.PLAY_ARROW, size=18, color=theme.surface),
                    ft.Text(
                        "立即播放第1集", size=18, color=theme.surface, weight="bold"
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            shadow=ft.BoxShadow(6, 13, theme.on_primary),
        )

        self.favoritemkv = ft.Container(
            height=46,
            border_radius=23,
            bgcolor=theme.surface_variant,
            padding=ft.Padding.symmetric(horizontal=24),
            content=ft.Row(
                controls=[
                    ft.Icon(
                        icon=ft.Icons.FAVORITE_SHARP, size=16, color=theme.on_surface
                    ),
                    ft.Text("收藏", size=16, color=theme.on_surface, weight="bold"),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            shadow=ft.BoxShadow(
                6, 13, ft.Colors.with_opacity(0.6, theme.surface_container_highest)
            ),
        )

        self.buttonline = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            controls=[self.playnow, self.favoritemkv],
            spacing=20,
            wrap=True,
        )

        super().__init__(
            col=configcol(xs=12, sm=9),
            padding=ft.Padding.symmetric(vertical=8, horizontal=20),
            content=ft.Column(
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.START,
                        controls=[self.bigTitle, self.subTitle],
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        wrap=True,
                    ),
                    self.score,
                    ft.Row(
                        controls=[self.markdown],
                    ),
                    ft.Divider(height=8, color=ft.Colors.with_opacity(0, "#000000")),
                    self.buttonline,
                ],
                spacing=15,
            ),
            **kwds,
        )

    def did_mount(self):
        self._mount = True
        return super().did_mount()

    def will_unmount(self):
        return super().will_unmount()

    def ScoreAppend(self, zone=None):
        if isinstance(zone, ft.Container):
            self.score.controls.append(zone)
            if self._mount:
                self.score.update()

    def ZoneTitle(
        self, value: str = None, size=18, color=theme.on_surface, **kwds
    ) -> ft.Container | None:
        if value:
            kwds.setdefault("padding", ft.Padding.symmetric(vertical=5, horizontal=12))
            kwds.setdefault("content", ft.Text(value, size=size, color=color))
            kwds.setdefault(
                "bgcolor", ft.Colors.with_opacity(0.5, theme.surface_container_highest)
            )
            kwds.setdefault("border_radius", 8)
            return ft.Container(**kwds)
        return None

    def update_bigtitle(self, title: str = None):
        if title and isinstance(title, str):
            self.bigTitle.value
            if self._mount:
                self.bigTitle.update()

    def update_markdown(self, mktex: str = None):
        if mktex and isinstance(mktex, str):
            self.markdown.value = textwrap.dedent(mktex)
            if self._mount:
                self.markdown.update()


# endregion
