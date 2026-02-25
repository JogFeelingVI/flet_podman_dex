# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-25 08:26:26

from .jackpot_core import randomData, filter_for_pabc
from .DraculaTheme import DraculaColors, RandColor
from .loger import logr
import flet as ft
import datetime
import os
import asyncio
import time
import re

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


# region Photograph


class Photograph(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__build__Container()
        self.visible = False
        self.padding = 12
        self.width = float("inf")
        self.border = ft.Border.all(
            1, ft.Colors.with_opacity(0.4, DraculaColors.ORANGE)
        )
        self.border_radius = 10

    def did_mount(self):
        self.running = True
        # print(f"Photograph did_mount. {self.running=}")
        self.initialization()

    def will_unmount(self):
        self.running = False

    def setting_get_exp_all(self, getexpall: list = None):
        self.get_exp_all = getexpall

    async def update_tips(self, text: str = ""):
        self.tips.value = f"{text}"
        self.tips.update()
        await asyncio.sleep(1)

    def initialization(self):
        is_mobile_or_web = self.page.web or self.page.platform in [
            ft.PagePlatform.ANDROID,
            ft.PagePlatform.IOS,
        ]
        self.conter.width = 400 if is_mobile_or_web else float("inf")

    def contentlist(self):
        self.neirong = ft.Column(
            tight=True,
            controls=[ft.Text("Photograph", size=16, color=RandColor())],
        )
        conters = ft.Container(
            padding=12,
            width=float("inf"),
            border=ft.Border(
                top=ft.BorderSide(1, ft.Colors.with_opacity(0.4, DraculaColors.ORANGE)),
                bottom=ft.BorderSide(
                    1, ft.Colors.with_opacity(0.4, DraculaColors.ORANGE)
                ),
            ),
            blend_mode=ft.BlendMode.OVERLAY,
            content=self.neirong,
        )
        return conters

    def footer(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.genid = randomData.generate_secure_string(8)
        return ft.Row(
            controls=[
                ft.Text(f"{now}-{self.genid}", size=14, color=DraculaColors.ORANGE)
            ],
            alignment=ft.MainAxisAlignment.END,
        )

    async def espcap_windows(self):
        count = 3
        while count > 0:
            await self.update_tips(f"The window will close in {count} seconds.")
            count -= 1
        self.visible = False
        self.update()

    def CreateItem(self, text: str = "", i=0):
        userColor = RandColor(mode="def")
        item = (
            ft.Container(
                padding=5,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.4, userColor)),
                bgcolor=ft.Colors.with_opacity(0.2, userColor),
                border_radius=5,
                content=ft.Row(
                    wrap=True,
                    width=float("inf"),
                    spacing=5,
                    controls=[
                        ft.Text(
                            f"{chr(65 + i)}: {text}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=userColor,
                            font_family="RacingSansOne-Regular",
                            # style=ft.TextStyle(
                            #     shadow=ft.BoxShadow(
                            #         blur_radius=1,  # 模糊程度，数值越大越像发光
                            #         color=ft.Colors.with_opacity(
                            #             0.2, "#ffffff"
                            #         ),  # 阴影颜色
                            #         offset=ft.Offset(1, 1),  # 阴影偏移量 (x, y)
                            #     )
                            # ),
                        ),
                    ],
                ),
            )
            if i >= 0
            else ft.Container(padding=5, height=10)
        )
        return item

    async def schot_exp_capture(self):
        if not self.running or not self.get_exp_all:
            self.update_tips("running is not or get_exp_all is None.")
            return
        exp_all = self.get_exp_all()
        if not exp_all:
            await self.update_tips("No data was obtained.")
            return
        await self.update_tips(f"Retrieve {len(exp_all)} data entries.")
        items = []
        for i, _exp in enumerate(exp_all):
            items.append(self.CreateItem(_exp, i))
            if (i + 1) % 5 == 0 and (i + 1) < len(_exp):
                items.append(self.CreateItem("", -1))
        self.neirong.controls = items
        self.visible = True
        self.update()
        # ? 这里可以考虑增加一个“正在生成图片”的提示，或者在外部调用这个函数前就显示提示，毕竟如果数据很多，生成图片可能需要一点时间
        is_mobile_or_web = self.page.web or self.page.platform in [
            ft.PagePlatform.ANDROID,
            ft.PagePlatform.IOS,
        ]
        try:
            image = await self.Screenshot.capture()
            png_name = f"{self.genid}.png"
            logr.info(f"{image.__sizeof__()=} {png_name=}")

            save_png = await ft.FilePicker().save_file(
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["png"],
                file_name=png_name,
                src_bytes=image,
            )
            logr.info(f"save_path: {save_png}")
            if save_png and not is_mobile_or_web:
                with open(save_png, "wb") as f:
                    f.write(image)
                await self.update_tips(f"Storage file directory {png_name}.")
            await self.update_tips(f"Storage task completed.")
        except Exception as er:
            await self.update_tips(f"Image saving error.")
        finally:
            await self.espcap_windows()

    def __build__Container(self):
        self.tips = ft.Text("Photograph", size=16, color=DraculaColors.ORANGE)
        self.title = ft.Text(
            "Jackpot Lotter",
            size=28,
            weight="bold",
            font_family="RacingSansOne-Regular",
            color=DraculaColors.ORANGE,
            italic=True,
        )
        self.footer = self.footer()
        self.conter = ft.Container(
            padding=12,
            bgcolor=DraculaColors.CURRENT_LINE,
            content=ft.Column(
                tight=True,
                spacing=0,
                controls=[
                    self.title,
                    self.contentlist(),
                    self.footer,
                ],
            ),
        )
        self.Screenshot = ft.Screenshot(content=self.conter)

        content = ft.Column(
            controls=[
                self.Screenshot,
                self.tips,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        )
        return content


# endregion


# region itemC2plus
class itemC2plus(ft.Container):
    def __init__(self):
        super().__init__()
        self.timeout = 30
        self.threshold = 120
        self.is_refreshing = False
        self.running = False
        self.state_exp = "none"  # "ref" "done"
        self.Itemc2_remove = None
        self.fontSize = 25
        self.selected = False
        # 参数
        self.userColor = RandColor()
        self.padding = 15
        self.border_radius = 10
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.4, self.userColor))
        self.bgcolor = ft.Colors.with_opacity(0.1, self.userColor)
        self.content = self.__build_content()

    def __build_tips(self):
        self.tips = ft.Text(
            value="Please wait...",
            no_wrap=True,
            size=13,
            color=ft.Colors.with_opacity(0.7, DraculaColors.FOREGROUND),
        )
        conta = ft.Container(
            content=self.tips,
            alignment=ft.Alignment.CENTER_RIGHT,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            # border=ft.Border.only(
            #     left=ft.BorderSide(5, ft.Colors.RED)  # 宽度为5的红色左边框
            # ),
            padding=ft.Padding.only(left=5),
            # 动画配置
            width=200,
        )
        return conta

    def tips_value(self, value: str, color: str = DraculaColors.FOREGROUND):
        self.tips.value = f"{value}"
        self.tips.color = ft.Colors.with_opacity(0.7, color)
        self.tips.tooltip = ft.Tooltip(message=f"{value}")
        # self.tips.update()

    def displayNumbers(self, text: str, size: int = 35):
        """用环形标示 标识出数字"""
        result = re.findall(r"\d+|\+", text)
        row = ft.Row(
            wrap=False,
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
            spacing=5,
        )
        colors = [["#d9dbdf", "#747fdf"], ["#eab425", "#fbbf24"]]
        quan, shuzi = colors[0]
        for key in result:
            if key == "+":
                quan, shuzi = colors[1]
                continue
            item = ft.Container(
                content=ft.Text(
                    value=f"{key}",
                    size=size * 0.5,  # 字体大小约为容器的一半
                    weight=ft.FontWeight.BOLD,
                    color=shuzi,  # 文字建议也用金色系或对比色
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=ft.Colors.TRANSPARENT,  # 背景透明
                border=ft.Border.all(1, quan),
                width=size,
                height=size,
                border_radius=size / 2,
                alignment=ft.Alignment.CENTER,
            )
            row.controls.append(item)
        return row

    def setting_adjust_position(self, adjustposition: None):
        self.adjust_position = adjustposition
        logr.info(f"setting adjustposition.")

    def did_mount(self):
        if not self.running and not self.is_refreshing and self.state_exp != "done":
            self.refresh(name="did_mount")

    def will_unmount(self):
        self.running = False

    def __build__badge(self, size: int = 20, text: str = "111"):
        self.buildBadge = ft.Container(
            content=ft.Text(
                f"{text}",
                size=size * 0.5,
                weight="bold",
                color=DraculaColors.FOREGROUND,
                text_align=ft.TextAlign.CENTER,
            ),
            padding=ft.Padding(8, 5, 8, 5),
            # width=size,
            # height=size,
            bgcolor=DraculaColors.RED,
            border_radius=size / 2,  # 半径设为宽高的一半即为正圆
            # alignment=ft.Alignment.CENTER,  # 确保图标在内部居中
        )
        return self.buildBadge

    def __build_check(self, size: int = 30):
        def toggle_icon(e):
            # 切换选中状态
            if self.state_exp != "done":
                return
            # e.control.selected = not e.control.selected
            # e.control.update()
            self.selected = not self.selected
            self.check.bgcolor = (
                ft.Colors.with_opacity(0.6, DraculaColors.GREEN)
                if self.selected
                else None
            )
            rows: ft.Column = self.content
            rows.controls[1].visible = not self.selected
            if self.adjust_position and self.selected:
                self.adjust_position(self)
                logr.info("adjust_position is self.")
            self.update()
            # end

        self.check = ft.Container(
            padding=5,
            content=ft.Icon(
                ft.Icons.CHECK, color=DraculaColors.FOREGROUND, size=size * 0.6
            ),
            width=size,
            height=size,
            border_radius=size / 2,
            alignment=ft.Alignment.CENTER,
            on_click=toggle_icon,
        )
        return self.check

    def __build_Butter(self, size=30, icon=ft.Icons.REFRESH, onclick=None):
        butter = ft.Container(
            # padding=5,
            content=ft.Icon(icon, color=self.userColor, size=size),
            # width=size,
            # height=size,
            # border_radius=size / 2,
            # alignment=ft.Alignment.CENTER,
            on_click=onclick,
        )
        return butter

    def __build_content(self):
        content = ft.Column(
            spacing=0,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    expand=1,
                    controls=[
                        shownumber := self.displayNumbers("05 06 07"),
                        self.__build_check(),
                    ],
                ),
                ft.Row(
                    expand=1,
                    spacing=5,
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        self.__build_tips(),
                        self.__build_Butter(
                            26, ft.Icons.REFRESH, self.handle_refresh_data
                        ),
                        self.__build_Butter(
                            26, ft.Icons.DELETE_FOREVER, self.handle_delete
                        ),
                        self.__build__badge(text="0"),
                    ],
                ),
            ],
        )
        self.showNumber = shownumber
        return content

    def setting_Itemc2_Remove(self, itemc2remove=None):
        self.Itemc2_remove = itemc2remove

    def refresh(self, name: str = "None"):
        if self.is_refreshing or self.selected:
            return
        # logr.info(f"markdata is running. {name}")
        self.page.run_task(self.SearchForData, name)

    # region SearchForData
    async def SearchForData(self, name: str):
        logr.info(f"SearchForData {name}")
        self.is_refreshing = True
        count = 0
        time
        await asyncio.sleep(0.5)
        start_time = time.time()
        try:
            while True:
                # 1. 使用 to_thread 运行耗时计算，防止界面卡死
                # 假设 calculate_lottery 是普通的同步函数
                # tempd, state = await asyncio.to_thread(self.calculate_lottery)
                tempd, state = await asyncio.to_thread(self.calculate_lottery)
                if state:
                    # 成功情况
                    self.tempd = tempd
                    self.showNumber.controls = self.displayNumbers(tempd).controls
                    self.tips_value("Search successful.", DraculaColors.GREEN)
                    self.state_exp = "done"
                    self.update()
                    break  # 成功后直接跳出循环
                else:
                    # 失败但未达到上限，更新 UI 并稍作等待
                    self.showNumber.controls = self.displayNumbers(tempd).controls
                    # self.showNumber.color = DraculaColors.ORANGE
                    self.buildBadge.content.value = f"{count}"
                    self.tips_value(
                        "We are searching diligently, please wait...",
                        DraculaColors.ORANGE,
                    )
                    self.state_exp = "ref"
                    self.update()
                    await asyncio.sleep(0.1)  # 给 CPU 喘息时间，也让 UI 有机会渲染
                count += 1
                elapsed_time = time.time() - start_time
                if elapsed_time >= self.timeout:
                    self.tips_value(
                        "Count is max_retries, work stoping.", DraculaColors.RED
                    )
                    self.state_exp = "none"
                    self.update()
                    break
        except Exception as e:
            # 显示错误/超时界面
            self.tips_value("Program execution error.", DraculaColors.YELLOW)
            self.update()
        finally:
            self.is_refreshing = False

    # endregion

    def calculate_lottery(self):
        settings = self.page.session.store.get("settings")
        filters = self.page.session.store.get("filters")
        if settings:
            rd = randomData(seting=settings["randomData"])
        else:
            return ("No settings", False)
        result = rd.get_pabc()
        if not filters:
            return (rd.get_exp(result), True)
        filter_jp = filter_for_pabc(filters=filters)
        if filter_jp.handle(result) == False:
            return (rd.get_exp(result), False)
        return (rd.get_exp(result), True)

    def handle_refresh_data(self, e):
        """右滑逻辑：刷新数据"""
        logr.info("向右滑动：正在刷新数据...")
        self.refresh(name="refresh_data")
        self.page.show_dialog(ft.SnackBar(f"handle refresh data."))

    def handle_delete(self, e):
        if self.is_refreshing or self.selected:
            return
        if self.Itemc2_remove:
            self.Itemc2_remove(self)
        self.page.show_dialog(ft.SnackBar(f"handle delete."))


# endregion


# region itemsList
class itemsList(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__build_card()
        self.max_item = 10
        self.padding = 10
        self.width = float("inf")
        self.bgcolor = ft.Colors.TRANSPARENT

    def did_mount(self):
        self.running = True
        self.find_the_maximum()

    def will_unmount(self):
        self.running = False

    def find_the_maximum(self):
        is_mobile_or_web = self.page.web or self.page.platform in [
            ft.PagePlatform.ANDROID,
            ft.PagePlatform.IOS,
        ]
        self.max_item = 10 if is_mobile_or_web else 1000

    def adjust_position(self, item: itemC2plus):
        if not item:
            return
        control: ft.Column = self.content
        control.controls.remove(item)
        control.controls.insert(0, item)
        control.update()
        logr.info("adjust_position is Done.")

    def add_itemc2(self, itemc2remove=None):
        control = self.content
        if not isinstance(control, ft.Column):
            logr.info(f"add_item type {type(control)}")
            return
        itemc2_len = [
            x
            for x in control.controls
            if isinstance(x, itemC2plus) and x.selected == False
        ].__len__()
        if itemc2_len < self.max_item:
            temp = itemC2plus()
            temp.setting_adjust_position(self.adjust_position)
            temp.setting_Itemc2_Remove(itemc2remove)
            control.controls.append(temp)
            self.update()

    def all_refresh(self):
        """全部刷新"""
        control = self.content
        if not isinstance(control, ft.Column):
            logr.info(f"all_refresh {type(control)}")
            return
        itemc2_all = [x for x in control.controls if isinstance(x, itemC2plus)]
        for item in itemc2_all:
            if item.selected == False:
                item.refresh(name="all_refresh")

    def get_item_exp(self):
        """"""
        control = self.content
        if not isinstance(control, ft.Column):
            logr.info(f"all_refresh {type(control)}")
            return
        exp_all = [
            x.tempd
            for x in control.controls
            if isinstance(x, itemC2plus) and x.selected
        ]
        return exp_all

    def remove_item(self, item: itemC2plus):
        control = self.content
        if not isinstance(control, ft.Column):
            return
        if item:
            control.controls.remove(item)
            self.update()

    def __build_card(self):
        """Add, Apply, Cancel"""
        return ft.Column(
            # wrap=True,
            controls=[],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
        )


# endregion


# region commandList
class commandList(ft.Container):
    def __init__(self):
        super().__init__()
        # self.content = self.__build_card()、
        self.padding = 12
        self.width = float("inf")
        # width=400,
        # self.border=ft.Border.all(1, DraculaColors.COMMENT)
        self.bgcolor = ft.Colors.TRANSPARENT
        # self.border_radius=10
        self.content = self.__command_button()
        # 基本属性
        self.item_list_add = None
        self.itemc2remove = None
        self.all_refresh = None
        self.shot_capture = None

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def setting_shot_capture(self, capture=None):
        self.shot_capture = capture

    def setting_item_list_add(self, itemlistadd=None, itemc2remove=None):
        self.item_list_add = itemlistadd
        self.itemc2remove = itemc2remove

    def setting_all_refresh(self, all_refresh=None):
        self.all_refresh = all_refresh

    def __build_butter(self, size=70, icon=ft.Icons.ABC, name="ABC", oncilck=None):
        def handle_hover(e):
            if e.data:
                conter.bgcolor = ft.Colors.with_opacity(0.2, DraculaColors.PURPLE)
                conter.border = ft.Border.all(
                    1, ft.Colors.with_opacity(0.4, DraculaColors.PURPLE)
                )
            else:
                conter.bgcolor = None
                conter.border = ft.Border.all(
                    1, ft.Colors.with_opacity(0.2, DraculaColors.PURPLE)
                )
            conter.update()

        def handle_onclick(e):
            if oncilck:
                oncilck(e)
            # Event(name='hover', data=True)
            handle_hover(ft.Event(name="hover", control=conter, data=False))

        # end

        conter = ft.Container(
            width=size,
            height=size,
            alignment=ft.Alignment.CENTER,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, DraculaColors.PURPLE)),
            border_radius=8,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, size=size * 0.45, color=DraculaColors.PURPLE),
                    ft.Text(
                        value=f"{name.upper()}",
                        size=size * 0.15,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
            on_hover=handle_hover,
            on_click=handle_onclick,
        )
        return conter

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Row(
            controls=[
                self.__build_butter(
                    icon=ft.Icons.INSERT_EMOTICON, name="ADD", oncilck=self.handle_add
                ),
                self.__build_butter(
                    icon=ft.Icons.REFRESH, name="Refresh", oncilck=self.handle_refresh
                ),
                self.__build_butter(
                    icon=ft.Icons.SAVE_AS, name="Export", oncilck=self.handle_export
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )

    def handle_export(self, e):
        if self.shot_capture:
            self.page.run_task(self.shot_capture)

    def handle_add(self, e):
        """执行add"""
        if self.item_list_add and self.itemc2remove:
            self.item_list_add(self.itemc2remove)

    def handle_refresh(self, e):
        if self.all_refresh:
            self.all_refresh()


# endregion


# region luck_tips
class lucktips(ft.Container):
    def __init__(self):
        super().__init__()
        self.bgcolor = ft.Colors.TRANSPARENT
        self.width = float("inf")
        self.padding = 10
        self.content = self.__build_tips()

    def __build_text(self, text: str = "Luck word."):
        return ft.Text(
            value=f"{text}",
            size=15,
            color=ft.Colors.with_opacity(0.5, DraculaColors.FOREGROUND),
            max_lines=2,
        )

    def __build_tips(self):
        content = ft.Column(
            controls=[
                self.__build_text(
                    "愿你所有的好运都不期而遇，愿你所有的努力都有岁月的温柔回馈。✨"
                ),
                self.__build_text(
                    "May all the good luck come to you unexpectedly, and may all your hard work be rewarded with the gentleness of time. 🕊️"
                ),
            ],
        )
        return content


# endregion


# region LotteryPage
class LotteryPage:
    def __init__(self):
        self.Photograph = Photograph()
        self.itemslist = itemsList()
        self.comandlist = commandList()
        # self.serendipitous_Capture = serendipitousCapture()

        self.Photograph.setting_get_exp_all(self.itemslist.get_item_exp)
        self.comandlist.setting_item_list_add(
            self.itemslist.add_itemc2, self.itemslist.remove_item
        )
        self.comandlist.setting_shot_capture(self.Photograph.schot_exp_capture)
        self.comandlist.setting_all_refresh(self.itemslist.all_refresh)
        self.luckTips = lucktips()
        self.view = self.get_data_view()

    # region get_data_view
    def get_data_view(self):
        return ft.Column(
            controls=[
                ft.Text(
                    "Lotter",
                    size=25,
                    weight="bold",
                    color=DraculaColors.COMMENT,
                    font_family="RacingSansOne-Regular",
                ),
                ft.Divider(),
                self.luckTips,
                self.itemslist,
                self.comandlist,
                self.Photograph,
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )

    # endregion


# endregion
