# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-02 09:10:57
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-05 07:16:33
import datetime
from .jackpot_core import randomData, filter_for_pabc
from .DraculaTheme import DraculaColors, RandColor
import asyncio
import flet as ft


# region savedialog
class savedialog(ft.AlertDialog):
    def __init__(self):
        super().__init__()
        self.modal = True
        self.content = self.__build_contens()
        self.actions = self.__build_action()
        self.content_padding = ft.Padding.all(15)

        self.running = False
        self.exps_is_build = True
        self.getallexp = None

    def __build_contens(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.genid = randomData.generate_secure_string(8)
        footer = ft.Row(
            controls=[
                ft.Text(f"{now} {self.genid}", size=14, color=DraculaColors.ORANGE)
            ],
            alignment=ft.MainAxisAlignment.END,
        )
        title = ft.Text(
            "Jackpot Lotter",
            size=28,
            weight="bold",
            font_family="RacingSansOne-Regular",
            color=DraculaColors.ORANGE,
            italic=True,
        )
        self.exps = ft.Column(
            spacing=5,
        )
        conter = ft.Container(
            width=400,
            padding=5,
            border_radius=0,
            bgcolor=DraculaColors.BACKGROUND,
            content=ft.Column(
                tight=True,
                spacing=5,
                controls=[
                    title,
                    self.exps,
                    footer,
                ],
            ),
        )
        self.Screenshot = ft.Screenshot(content=conter)
        content = ft.Column(
            controls=[self.Screenshot],
            tight=True,
        )
        return content

    def __build_action(self):
        acts = [
            ft.TextButton(
                "Cancel",
                on_click=self.__handle_no,
                style=ft.ButtonStyle(color=RandColor()),
            ),
            # 确定按钮用红色突出显示危险操作
            ft.TextButton(
                "Save to png",
                on_click=self.__handle_yes,
                style=ft.ButtonStyle(color=RandColor()),
            ),
        ]
        return acts

    def __handle_no(self, e):
        self.page.pop_dialog()

    async def __handle_yes(self, e):
        if self.exps_is_build:
            is_mobile_or_web = self.page.web or self.page.platform in [
                ft.PagePlatform.ANDROID,
                ft.PagePlatform.IOS,
            ]
            try:
                image = await self.Screenshot.capture()
                png_name = f"{self.genid}.png"
                # print(f"{image.__sizeof__()=} {png_name=}")

                save_png = await ft.FilePicker().save_file(
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=["png"],
                    file_name=png_name,
                    src_bytes=image,
                )
                # print(f"save_path: {save_png}")
                if save_png and not is_mobile_or_web:
                    with open(save_png, "wb") as f:
                        f.write(image)
                        self.page.show_dialog(
                            ft.SnackBar(f"{self.page.platform} file save complete.")
                        )
                # print(f"Storage task completed.")
            except Exception as er:
                # print(f"Image saving error.")
                pass
            finally:
                await asyncio.sleep(1)
                self.page.pop_dialog()

    def seting_get_all_exp(self, getallexp=None):
        self.getallexp = getallexp

    def did_mount(self):
        self.running = True
        self.page.run_task(self.load_exp)

    def will_unmount(self):
        self.running = False

    async def load_exp(self):
        self.exps_is_build = False
        if not self.getallexp:
            # print("not is getallexp func.")
            return
        all_exp = self.getallexp()
        if len(all_exp) == 0:
            # print("len all_exp is zero.")
            return
        items = []
        for i, _exp in enumerate(all_exp):
            items.append(self.CreateItem(_exp, i))
            if (i + 1) % 5 == 0 and (i + 1) < len(_exp):
                items.append(self.CreateItem("", -1))
        self.exps.controls = items
        self.exps.update()
        self.exps_is_build = True

    def CreateItem(self, text: str = "", i=0):
        userColor = RandColor(mode="def")
        asize = 18
        item = (
            ft.Container(
                padding=5,
                # border=ft.Border.all(1, ft.Colors.with_opacity(0.4, userColor)),
                bgcolor=ft.Colors.with_opacity(0.1, userColor),
                border_radius=5,
                content=ft.Row(
                    wrap=True,
                    width=float("inf"),
                    spacing=5,
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                f"{chr(65 + i)}",
                                size=asize * 0.6,
                                text_align=ft.TextAlign.CENTER,
                                color=DraculaColors.FOREGROUND,
                            ),
                            alignment=ft.Alignment.CENTER,
                            border_radius=asize / 2,
                            border=ft.Border.all(
                                1, ft.Colors.with_opacity(0.8, userColor)
                            ),
                            bgcolor=ft.Colors.with_opacity(0.2, userColor),
                            width=asize,
                            height=asize,
                        ),
                        ft.Text(
                            f"{text}",
                            size=asize,
                            weight=ft.FontWeight.BOLD,
                            color=userColor,
                        ),
                    ],
                ),
            )
            if i >= 0
            else ft.Container(padding=5, height=10)
        )
        return item


# endregion


# region test
class testdialog(ft.AlertDialog):
    def __init__(self):
        super().__init__()
        self.modal = True
        self.content = self.__build_contens()
        self.actions = self.__build_action()
        self.content_padding = ft.Padding.all(15)

        self.running = False

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def __handle_Close(self, e):
        if self.running:
            self.page.pop_dialog()

    def __handle_start(self, e):
        if self.running:
            self.page.run_task(self.start_testing)
            # self.page.pop_dialog()

    def __build_action(self):
        acts = [
            ft.TextButton(
                "Close",
                on_click=self.__handle_Close,
                style=ft.ButtonStyle(color=RandColor()),
            ),
            # 确定按钮用红色突出显示危险操作
            ft.TextButton(
                "Start testing",
                on_click=self.__handle_start,
                style=ft.ButtonStyle(color=RandColor()),
            ),
        ]
        return acts

    def __build_contens(self):
        title = ft.Text(
            "Filter test",
            size=28,
            weight="bold",
            font_family="RacingSansOne-Regular",
            color=DraculaColors.ORANGE,
            italic=True,
        )
        self.info_display = ft.Column(
            tight=True,
            spacing=5,
            controls=[
                self.info("Click the `Start testing` button to begin the test."),
            ],
        )
        conter = ft.Container(
            width=400,
            padding=5,
            border_radius=0,
            bgcolor=DraculaColors.BACKGROUND,
            content=ft.Column(
                tight=True,
                spacing=5,
                height=500,
                controls=[
                    title,
                    self.info_display,
                ],
                scroll=ft.ScrollMode.HIDDEN,
            ),
        )
        return conter

    def info(self, msg: str = None):
        if not msg:
            return
        info = ft.Text(f"{msg}", size=15, color=RandColor(mode="Glass"))
        return info
    
    #region start_testing
    async def start_testing(self):
        if not self.running:
            return
        settings = self.page.session.store.get("settings")
        filtersAll = self.page.session.store.get("filters")
        self.info_display.controls.clear()
        self.info_display.controls.append(
            self.info(f"The total number of filters is {len(filtersAll)}")
        )
        self.info_display.controls.append(
            self.info(f"Game Rules: {settings['randomData']['note']}")
        )
        
        if settings and filtersAll:
            _rdpn = randomData(seting=settings["randomData"])
            results = []
            for i in range(1000):
                results.append(_rdpn.get_pabc())
        self.info_display.controls.append(
            self.info(f"results len: {len(results)}")
        )
        self.info_display.update()
        for _fitem in filtersAll:
            print(f'{_fitem}')
            _f2func = filter_for_pabc(filters=[_fitem])
            pass_rate = sum([1 for r in results if _f2func.handle(r)])/len(results) * 100
            prinfo = f"{_fitem['func']} `{_fitem['target']}` -> `{_fitem['condition']}` PR [ {pass_rate:.2f}% ]"
            self.info_display.controls.append(self.info(f"{prinfo}"))
        self.info_display.update()
    # endregion


# endregion
