# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-15 06:10:20
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-16 23:43:36

from .DraculaTheme import DraculaColors
from .lotteryballs import LotteryBalls
from .jackpot_core import randomData, filter_for_pabc
import flet as ft
import json
import asyncio


def calculate_lottery(setings: dict, filters: list):
    if setings:
        rd = randomData(seting=setings)
    else:
        return ("No Numbers", False)
    result = rd.get_pabc()
    if not filters:
        return (rd.get_exp(result), True)
    filter_jp = filter_for_pabc(filters=filters)
    if filter_jp.handle(result) == False:
        return [rd.get_exp(result), False]
    return (rd.get_exp(result), True)


class dism(ft.Dismissible):
    def __init__(self):
        self.data = "05 12 18 23 35 + 06 12"
        self.dismiss_direction = ft.DismissDirection.HORIZONTAL
        self.running = False
        self.is_refreshing = False
        # self.confirm_dismiss = True
        super().__init__(
            content=self.__content(0),
            background=self.bgc(),
            secondary_background=self.sbgc(),
            dismiss_thresholds={
                ft.DismissDirection.END_TO_START: 0.2,
                ft.DismissDirection.START_TO_END: 0.2,
            },
            on_confirm_dismiss=self.handle_confirm_dismiss,
            # on_dismiss=self.handle_dismiss,
            key=randomData.generate_secure_string(8),
        )

    async def handle_confirm_dismiss(self, e: ft.DismissibleDismissEvent):
        """False 取消删除"""
        await e.control.confirm_dismiss(False)
        if e.direction == ft.DismissDirection.END_TO_START:  # right-to-left slide
            # save current dismissible to dialog's data, for confirmation in
            # reloading
            self.MarkData("handle_confirm_dismiss")
        elif e.direction == ft.DismissDirection.START_TO_END:
            # save data
            raw_json = await self.page.shared_preferences.get("save_data_list")
            save_list = json.loads(raw_json) if raw_json else []
            if e.control.data not in set(save_list):
                save_list.append(e.control.data)
                await self.page.shared_preferences.set(
                    "save_data_list", json.dumps(save_list)
                )

            # 执行外部程序，实现联动
            if self.badge_update:
                self.badge_update(len(save_list))

    def handle_dismiss(self, e):
        # 暂时不使用
        print(f"dismiss {e}")
        self.update()

    def setting_args(self, setting: dict, filter: list, badge_update=None):
        self.setting = setting
        self.filers = filter
        self.badge_update = badge_update

    def did_mount(self):
        if not self.running:
            self.MarkData("did mount")
            self.running = True
        return super().did_mount()

    def will_unmount(self):
        return super().will_unmount()

    def bgc(self):
        return ft.Container(
            content=ft.Text("Save", weight="bold"),
            bgcolor=DraculaColors.RED,
            alignment=ft.Alignment.CENTER_LEFT,
            padding=ft.Padding.only(left=20),
            border_radius=5,
        )

    def sbgc(self):
        return ft.Container(
            content=ft.Text("ReLoading", weight="bold"),
            bgcolor=DraculaColors.PURPLE,
            alignment=ft.Alignment.CENTER_RIGHT,
            padding=ft.Padding.only(right=20),
            border_radius=5,
        )

    def MarkData(self, name):
        if self.is_refreshing:
            return
        # print(f"markdata is running. {name}")
        self.page.run_task(self.refresh)

    def __content(self, flg):
        """
        根据标记来显示不同的 Container
        Args:
            flg (int): 运行标志
            1 装载 LotteryBalls 数据
            2 😡Press and hold to try again.
            0 😅Initializing the computing core.

        Returns:
            flet: ft.Container
        """
        _content = ft.Text("loading...")
        _row = ft.Row(
            controls=[
                ft.Text(
                    "😡Press and hold to try again.",
                    weight="bold",
                    size=18,
                    color=DraculaColors.PURPLE,
                )
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            align=ft.Alignment.CENTER,
        )
        _row_setting_text = lambda _T, _C: setattr(_C.controls[0], "value", _T)
        _content = None
        # print(f"debug: {flg=}")
        match flg:
            case 1:
                _content = LotteryBalls(self.data, 29, "LE")
            case 2:
                _content = _row
                _row_setting_text("😡Press and hold to try again.", _content)
            case 0:
                _content = _row
                _row_setting_text("😅Initializing the computing core.", _content)
            case _:
                _content = _row
                _row_setting_text("😅Loading...", _content)

        return ft.Container(
            padding=10,
            content=_content,
            alignment=ft.Alignment.CENTER_LEFT,
        )

    async def refresh(self):
        # print('refresh is now running.')
        self.is_refreshing = True
        count = 0
        max_retries = 100
        await asyncio.sleep(0.3)

        # 初始化界面为加载中状态（可选）
        # self.content = self.__content(正在加载的索引)
        # self.update()

        try:
            while count < max_retries:
                # 1. 使用 to_thread 运行耗时计算，防止界面卡死
                # 假设 calculate_lottery 是普通的同步函数
                tempd, state = await asyncio.to_thread(
                    calculate_lottery, setings=self.setting, filters=self.filers
                )

                if state:
                    # 成功情况
                    self.data = tempd
                    self.content = self.__content(1)
                    self.update()
                    break  # 成功后直接跳出循环
                else:
                    # 失败但未达到上限，更新 UI 并稍作等待
                    self.data = tempd
                    self.content = self.__content(1)
                    self.update()
                    await asyncio.sleep(0.3)  # 给 CPU 喘息时间，也让 UI 有机会渲染

                count += 1

                # 2. 超时处理
                if count >= max_retries:
                    print("count is max_retries, work stoping.")
                    self.content = self.__content(2)  # 显示错误/超时界面
                    self.update()
                    break

        except Exception as e:
            print(f"refresh is error: {e}")
            self.content = self.__content(2)
            self.update()
        finally:
            self.is_refreshing = False
            self.update()  # 确保最后刷新状态被重置


#! old
class listext_onlong(ft.Card):
    def __init__(self):
        super().__init__()
        self.data = "01 02 03 04 05 06 + 08"
        self.content = self.reContent(0)
        self.padding = 10
        # self.leading = ft.Icon(ft.Icons.GENERATING_TOKENS, color=DraculaColors.ORANGE)
        # self.subtitle = LotteryBalls(self.data,25)
        # self.on_long_press = lambda _: self.get_data(1, True)
        self.runing = True
        self.is_refreshing = False

    def reContent(self, flg: int = 0):
        """
            返回 Container
        Args:
            flg (int, optional): _description_. Defaults to 0.
            0 Initializing the computing core.
            2 Please try again later.
            1 LotteryBalls
        Returns:
            _type_: _description_

        """
        print(f"debug: {flg=}")
        content = ft.Text("loading...")
        match flg:
            case 1:
                content = LotteryBalls(self.data, 29, "LE")
            case 2:
                content = ft.Row(
                    controls=[
                        ft.Text(
                            "😡Press and hold to try again.",
                            weight="bold",
                            size=18,
                            color=DraculaColors.PURPLE,
                        )
                    ],
                    expand=True,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    align=ft.Alignment.CENTER,
                )
            case 0:
                content = ft.Row(
                    controls=[
                        ft.Text(
                            "😅Initializing the computing core.",
                            weight="bold",
                            size=18,
                            color=DraculaColors.CURRENT_LINE,
                        )
                    ],
                    expand=True,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    align=ft.Alignment.CENTER,
                )
            case _:
                pass

        # return ft.Container(
        #     padding=10,
        #     content=conten,
        #     alignment=ft.Alignment.CENTER_LEFT,
        #     animate_scale=ft.Animation(300, ft.AnimationCurve.DECELERATE),
        #     on_long_press=lambda _: self.get_data(1, True),
        # )
        _content = ft.Container(
            padding=10,
            content=content,
            alignment=ft.Alignment.CENTER_LEFT,
        )
        return _content

    def setting_args(self, setting: dict, filter: list):
        self.setting = setting
        self.filers = filter

    def did_mount(self):
        self.get_data(0)

    def will_unmount(self):
        self.runing = False

    def get_data(self, state: int = 1, onoff=False):
        # print(f'{self.content.scale=} {state=} {onoff=} {self.runing=}')
        if self.is_refreshing:
            return
        if state == 0 and self.runing:
            self.page.run_task(self.refresh)
        if state == 1 and onoff:
            self.content.scale = ft.Scale(1.2)
            self.content.update()
            self.page.run_task(self.refresh)

    async def refresh(self):
        isok = False
        note_error = 0
        self.is_refreshing = True
        await asyncio.sleep(0.3)
        try:
            while isok == False:
                tempd, state = calculate_lottery(
                    setings=self.setting, filters=self.filers
                )
                if state:
                    self.data = tempd
                    self.content = self.reContent(1)
                    isok = state
                else:
                    if note_error >= 100:
                        self.content = self.reContent(2)
                        self.page.update()
                        break
                    note_error += 1
                    self.data = tempd
                    self.content = self.reContent(1)
                self.update()
                await asyncio.sleep(0.1)
        finally:
            self.is_refreshing = False
