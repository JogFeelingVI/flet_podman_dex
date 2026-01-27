# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-26 14:44:04

import asyncio
from .jackpot_core import randomData, filter_for_pabc
from .lotteryballs import LotteryBalls
from .SnackBar import get_snack_bar
from .DraculaTheme import DraculaColors
import flet as ft
import datetime
import os

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


class serendipitousCapture(ft.Card):
    """创建一个控件 用来使用列表拍照"""

    def __init__(self):
        super().__init__()
        self.get_exp_all = None
        self.scshot = self.__build_exp()
        self.tips = self.__build_tips()
        self.content = self.__build__Container()
        self.visible = False

    def setting_get_exp_all(self, getexpall: list = None):
        self.get_exp_all = getexpall

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    async def update_tips(self, text: str = ""):
        self.tips.value = f"{text}"
        self.tips.update()
        await asyncio.sleep(1)

    async def espcap_windows(self):
        for i in range(1, 4):
            await self.update_tips(f"The window will close in {3 - i} seconds.")

    async def add_exp(self, exp: list = None, genid: str = None):
        if not exp:
            return
        exp_show = self.scshot.content.content
        if not isinstance(exp_show, ft.Column):
            return
        if not genid:
            return
        esc = [x for x in exp_show.controls if x.data == "biaoyu"]
        esc.append(ft.Divider(color="#7b0000"))
        for i, _e in enumerate(exp):
            esc.append(
                ft.Text(
                    value=f"{chr(65 + i)}: {_e}",
                    size=18,
                    color="#900015" if i % 2 == 0 else "#d7a700",
                    weight="bold",
                )
            )
            if (i + 1) % 5 == 0:
                esc.append(ft.Divider(color=ft.Colors.TRANSPARENT))
        esc.append(ft.Divider(color="#7b0000"))
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        esc.append(
            ft.Text(
                value=f"{now} {genid}",
                size=12,
                color="#7b0000",
            )
        )
        exp_show.controls = esc
        exp_show.update()

    async def schot_exp_capture(self):
        try:
            self.visible = True
            self.update()
            if not self.running:
                await self.update_tips("running is not.")
                return
            if not self.get_exp_all:
                await self.update_tips("No data to capture.")
                return
            exp_all = self.get_exp_all()
            if not exp_all:
                await self.update_tips("No data was obtained.")
                return
            await self.update_tips(f"Retrieve {len(exp_all)} data entries.")
            genid = randomData.generate_secure_string(8)
            await self.add_exp(exp_all, genid)
            # 2. 获取存储路径 (建议使用 page.client_storage)
            if self.page.web:
                stored_dir = app_data_path
            else:
                stored_dir = await ft.SharedPreferences().get("user_dir")
            if not stored_dir:
                await self.update_tips("No storage directory found.")
                return
            await self.update_tips(f"Confirm the storage directory {stored_dir}.")

            # 4. 【非常重要】截图控件必须先添加到页面上
            # 我们把它放到 overlay 中，这样它就存在于页面树中，但不会破坏现有布局
            image = await self.scshot.capture()
            obj_path = os.path.join(stored_dir, f"jackpot_{genid}.png")
            await self.update_tips(f"Storage file directory {obj_path}.")

            with open(obj_path, "wb") as f:
                f.write(image)
            await self.update_tips(f"Storage task completed.")

        except Exception as e:
            print(f"Capture error: {e}")
        finally:
            self.visible = False
            await self.espcap_windows()
            self.update()

    def __build_tips(self):
        return ft.Text("save to ...", size=16, color=DraculaColors.ORANGE)

    def __build_exp(self):
        return ft.Screenshot(
            content=ft.Container(
                foreground_decoration=ft.BoxDecoration(
                    # bgcolor=DraculaColors.CURRENT_LINE,
                    image=ft.DecorationImage(
                        src="fa.png",
                        fit=ft.BoxFit.NONE,
                        # repeat=ft.ImageRepeat.REPEAT,
                        opacity=0.1,
                    ),
                ),
                bgcolor="#1f1f1f",
                border_radius=5,
                padding=10,
                content=ft.Column(
                    spacing=5,
                    controls=[
                        ft.Text(
                            "May your cup overflow with blessings and your coffers with gold.",
                            size=16,
                            color="#7b0000",
                            italic=True,
                            data="biaoyu",
                        ),
                    ],
                ),
            ),
        )

    def __build__Container(self):
        # 注意：这里 self.exp_list 已经是字符串或列表，逻辑保持你的不变
        return ft.Container(
            padding=12,
            width=float("inf"),
            # width=600,
            border=ft.Border.all(2, DraculaColors.ORANGE),
            border_radius=10,
            content=ft.Column(
                controls=[
                    self.scshot,
                    ft.Divider(),
                    self.tips,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
        )


class ItemC2(ft.GestureDetector):
    """支持左右滑动操作的项目条目"""

    def __init__(self):
        super().__init__()

        # 用于记录累积的滑动距离
        self.drag_accumulated = 0
        # 触发动作的阈值（滑动超过 100 像素则触发）
        self.threshold = 100
        self.is_refreshing = False
        self.running = False
        self.state_exp = "none"  # "ref" "done"
        self.Itemc2_remove = None

        self.red_glow = ft.BoxShadow(
            blur_radius=25,  # 阴影模糊程度（数值越大越柔和）
            spread_radius=2,  # 阴影扩散范围
            color=ft.Colors.with_opacity(0.6, ft.Colors.RED),  # 红色半透明
            blur_style=ft.BlurStyle.NORMAL,
        )

        self.blue_glow = ft.BoxShadow(
            blur_radius=25,  # 阴影模糊程度（数值越大越柔和）
            spread_radius=2,  # 阴影扩散范围
            color=ft.Colors.with_opacity(0.6, ft.Colors.BLUE),  # 红色半透明
            blur_style=ft.BlurStyle.NORMAL,
        )

        # 1. 构建内部显示的 Chip
        self.chip_content = ft.Text(
            "03 07 11 17 29 30 + 09", size=20, color=DraculaColors.PURPLE
        )
        self.chip = ft.Chip(
            width=float("inf"),
            label=ft.Container(
                content=self.chip_content,
                alignment=ft.Alignment.CENTER_LEFT,
                expand=True,
                animate=ft.Animation(300, ft.AnimationCurve.DECELERATE),
            ),
            shape=ft.RoundedRectangleBorder(radius=8),
            bgcolor=DraculaColors.CURRENT_LINE,  # 替换为你的 DraculaColors.CURRENT_LINE
            selected_color=DraculaColors.COMMENT,
            on_delete=self.handle_delete,
            on_select=self.handle_select,  # 处理点击事件
            # 注意：在 GestureDetector 下，Chip 的 on_select 可能会干扰手势，
            # 建议点击事件统一由 GestureDetector 处理
        )

        # 2. 设置 GestureDetector 的属性
        self.content = self.chip
        self.on_horizontal_drag_update = self.handle_drag_update
        self.on_horizontal_drag_end = self.handle_drag_end

    def setting_Itemc2_Remove(self, itemc2remove=None):
        self.Itemc2_remove = itemc2remove

    def did_mount(self):
        if not self.running and not self.is_refreshing and self.state_exp != "done":
            self.refresh(name="did_mount")

    def will_unmount(self):
        self.running = False

    def refresh(self, name: str = "None"):
        if self.is_refreshing or self.chip.selected:
            return
        # print(f"markdata is running. {name}")
        self.page.run_task(self.SearchForData, name)

    async def SearchForData(self, name: str):
        print(f"SearchForData {name}")
        self.is_refreshing = True
        count = 0
        max_retries = 100
        await asyncio.sleep(0.5)
        try:
            while count < max_retries:
                # 1. 使用 to_thread 运行耗时计算，防止界面卡死
                # 假设 calculate_lottery 是普通的同步函数
                # tempd, state = await asyncio.to_thread(self.calculate_lottery)
                tempd, state = await asyncio.to_thread(self.calculate_lottery)
                if state:
                    # 成功情况
                    self.chip_content.value = tempd
                    self.chip_content.color = DraculaColors.PURPLE
                    self.state_exp = "done"
                    self.update()
                    print("Search successful")
                    break  # 成功后直接跳出循环
                else:
                    # 失败但未达到上限，更新 UI 并稍作等待
                    self.chip_content.value = f"refresh {tempd}"
                    self.chip_content.color = DraculaColors.ORANGE
                    self.state_exp = "ref"
                    self.update()
                    await asyncio.sleep(0.3)  # 给 CPU 喘息时间，也让 UI 有机会渲染
                count += 1
                if count >= max_retries:
                    print("count is max_retries, work stoping.")
                    self.chip_content.value = (
                        "Please swipe right to restart."  # 显示错误/超时界面
                    )
                    self.chip_content.color = DraculaColors.RED
                    self.state_exp = "none"
                    self.update()
                    break
        except Exception as e:
            self.chip_content.value = "Find data errors."  # 显示错误/超时界面
            self.update()
        finally:
            self.is_refreshing = False

    def calculate_lottery(self):
        settings = self.page.session.store.get("settings")
        filters = self.page.session.store.get("filters")
        if settings:
            rd = randomData(seting=settings["randomData"])
        else:
            return ("No Numbers", False)
        result = rd.get_pabc()
        if not filters:
            return (rd.get_exp(result), True)
        filter_jp = filter_for_pabc(filters=filters)
        if filter_jp.handle(result) == False:
            return [rd.get_exp(result), False]
        return (rd.get_exp(result), True)

    def handle_drag_update(self, e: ft.DragUpdateEvent):
        # 累加滑动距离 (e.primary_delta 在水平滑动时是 x 轴的变化量)
        self.drag_accumulated += e.primary_delta

    def handle_drag_end(self, e: ft.DragEndEvent):
        # 判断滑动方向
        if self.drag_accumulated > self.threshold:
            self.refresh_data()
        elif self.drag_accumulated < -self.threshold:
            self.save_item()

        # 重置滑动计数值
        self.drag_accumulated = 0

    def refresh_data(self):
        """右滑逻辑：刷新数据"""
        print("向右滑动：正在刷新数据...")
        self.refresh(name="refresh_data")

    def save_item(self):
        """左滑逻辑：保存项目"""
        print("向左滑动：项目已保存")
        # 这里执行你的保存逻辑
        self.page.show_dialog(ft.SnackBar(ft.Text("项目已保存！")))

    async def handle_select(self, e):
        if self.is_refreshing:
            self.chip.selected = False
            return
        if self.state_exp != "done":
            self.chip.selected = False
            return
        # raw_json = await ft.SharedPreferences().get("save_data_list")
        # save_list = json.loads(raw_json) if raw_json else []
        # if  self.chip_content.value not in set(save_list):
        #     save_list.append(self.chip_content.value)
        #     await ft.SharedPreferences().set(
        #         "save_data_list", json.dumps(save_list)
        #     )

        self.update()

    def handle_delete(self, e):
        if self.is_refreshing or self.chip.selected:
            return
        if self.Itemc2_remove:
            self.Itemc2_remove(self)
        self.chip.update()
        print("点击了删除图标")


#
#
# OLD
#
#
class itemsList(ft.Card):
    def __init__(self):
        super().__init__()
        self.content = self.__build_card()
        self.max_item = 10

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def __build_card(self):
        return ft.Container(
            padding=12,
            width=float("inf"),
            # width=400,
            border=ft.Border.all(2, DraculaColors.PINK),
            border_radius=10,
            content=self.__command_button(),
        )

    def add_itemc2(self, itemc2remove=None):
        control = self.content.content
        if not isinstance(control, ft.Column):
            print(f"add_item type {type(control)}")
            return
        itemc2_len = [x for x in control.controls if isinstance(x, ItemC2)].__len__()
        if itemc2_len < self.max_item:
            temp = ItemC2()
            temp.setting_Itemc2_Remove(itemc2remove)
            control.controls.append(temp)
            print("Add ItemC2")
            self.update()

    def all_refresh(self):
        """全部刷新"""
        control = self.content.content
        if not isinstance(control, ft.Column):
            print(f"all_refresh {type(control)}")
            return
        itemc2_all = [x for x in control.controls if isinstance(x, ItemC2)]
        for item in itemc2_all:
            if item.chip.selected == False:
                item.refresh(name="all_refresh")

    def get_item_exp(self):
        """"""
        control = self.content.content
        if not isinstance(control, ft.Column):
            print(f"all_refresh {type(control)}")
            return
        exp_all = [
            x.chip_content.value
            for x in control.controls
            if isinstance(x, ItemC2) and x.chip.selected
        ]
        return exp_all

    def remove_item(self, item: ItemC2):
        control = self.content.content
        if not isinstance(control, ft.Column):
            return
        if item:
            control.controls.remove(item)
            self.update()

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Column(
            # wrap=True,
            controls=[
                ft.Text(
                    "愿你所有的好运都不期而遇，愿你所有的努力都有岁月的温柔回馈。✨"
                ),
                ft.Text(
                    "May all the good luck come to you unexpectedly, and may all your hard work be rewarded with the gentleness of time. 🕊️"
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
        )


#! class commandlist
class commandList(ft.Card):
    def __init__(self):
        super().__init__()
        self.content = self.__build_card()
        self.item_list_add = None
        self.itemc2remove = None
        self.all_refresh = None
        self.shot_capture = None

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def __build_card(self):
        return ft.Container(
            padding=12,
            width=float("inf"),
            # width=400,
            border=ft.Border.all(2, DraculaColors.COMMENT),
            border_radius=10,
            content=self.__command_button(),
        )

    def setting_shot_capture(self, capture=None):
        self.shot_capture = capture

    def setting_item_list_add(self, itemlistadd=None, itemc2remove=None):
        self.item_list_add = itemlistadd
        self.itemc2remove = itemc2remove

    def setting_all_refresh(self, all_refresh=None):
        self.all_refresh = all_refresh

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Row(
            controls=[
                ft.TextButton(
                    expand=1,
                    key="add_close",
                    icon=ft.Icons.INSERT_EMOTICON,
                    content="Add",
                    on_click=self.handle_add,
                ),
                ft.TextButton(
                    expand=1,
                    icon=ft.Icons.REFRESH,
                    content="Refresh",
                    on_click=self.handle_refresh,
                ),
                ft.TextButton(
                    expand=1,
                    icon=ft.Icons.SAVE_AS,
                    content="Export",
                    on_click=self.handle_export,
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def handle_export(self):
        if self.shot_capture:
            self.page.run_task(self.shot_capture)

    def handle_add(self):
        """执行add"""
        if self.item_list_add and self.itemc2remove:
            self.item_list_add(self.itemc2remove)

    def handle_refresh(self):
        if self.all_refresh:
            self.all_refresh()


#! class LotteryPage


class LotteryPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.itemslist = itemsList()
        self.comandlist = commandList()
        self.serendipitous_Capture = serendipitousCapture()

        self.serendipitous_Capture.setting_get_exp_all(self.itemslist.get_item_exp)
        self.comandlist.setting_item_list_add(
            self.itemslist.add_itemc2, self.itemslist.remove_item
        )
        self.comandlist.setting_shot_capture(
            self.serendipitous_Capture.schot_exp_capture
        )
        self.comandlist.setting_all_refresh(self.itemslist.all_refresh)
        self.view = self.get_data_view()

    # async def inisatll_save_dig(self, e):
    #     raw_json = await ft.SharedPreferences().get("save_data_list")
    #     saved_data = json.loads(raw_json) if raw_json else []
    #     print(f"kaishi Save. {saved_data=}")
    #     if saved_data.__len__() == 0:
    #         self.page.show_dialog(get_snack_bar("No data to save.", "error"))
    #         return
    #     sbms = sbbdismiss(saved_data)
    #     saved_data = sbms.External_data
    #     items = sbms.items

    #     async def handle_save(e):
    #         e.control.disabled = True
    #         self.page.update()
    #         path = await self.select_dir()
    #         if not path:
    #             print("No directory was selected; saving cancelled.")
    #             e.control.disabled = False
    #             self.page.update()
    #             return
    #         print(f"select dir is {self.user_dir=}")
    #         await self.save_screenshot(sc, path, genid)
    #         nonlocal items
    #         items.clear()
    #         # await self.initialize_data()
    #         await asyncio.sleep(0.5)
    #         self.Badge_number(0)
    #         e.control.disabled = False
    #         BottomSheet.open = False
    #         # self.page.update()

    #     def handle_cancel(e):
    #         BottomSheet.open = False
    #         self.page.update()

    #     def handle_clear(e):
    #         print("Clear all saved data.")
    #         nonlocal items
    #         items.clear()
    #         self.Badge_number(0)
    #         BottomSheet.open = False

    #     genid = randomData.generate_secure_string(8)

    #     sc = ft.Screenshot(
    #         content=ft.Container(
    #             content=ft.Column(
    #                 tight=True,
    #                 horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    #                 opacity=1.0,
    #                 controls=[
    #                     # ft.Text(
    #                     #     value="JackPot",
    #                     #     size=30,
    #                     #     weight=ft.FontWeight.W_900,
    #                     #     color=DraculaColors.PINK,
    #                     # ),
    #                     # ? 添加图片
    #                     ft.Row(
    #                         controls=[
    #                             ft.Image(
    #                                 src="jackpot.png",
    #                                 fit=ft.BoxFit.FIT_HEIGHT,
    #                                 width=397 * 0.45,
    #                                 height=127 * 0.45,
    #                             ),
    #                         ],
    #                         alignment=ft.MainAxisAlignment.START,
    #                     ),
    #                     ft.Divider(color=DraculaColors.PURPLE),
    #                     sbms,
    #                     ft.Row(
    #                         controls=[
    #                             ft.Text(
    #                                 value=f"GENID: {genid}",
    #                                 size=15,
    #                                 weight=ft.FontWeight.W_100,
    #                                 color=DraculaColors.BACKGROUND,
    #                             ),
    #                         ],
    #                         alignment=ft.MainAxisAlignment.START,  # 关键点：主轴对齐到末尾
    #                     ),
    #                 ],
    #             ),
    #             bgcolor=DraculaColors.CURRENT_LINE,
    #             padding=20,
    #             width=400,
    #             # height=680,
    #             alignment=ft.Alignment.TOP_CENTER,
    #         )
    #     )
    #     savebut = ft.Container(
    #         content=ft.Row(
    #             controls=[
    #                 ft.TextButton(
    #                     content="Save",
    #                     on_click=handle_save,
    #                 ),
    #                 ft.TextButton(
    #                     content="Cancel",
    #                     on_click=handle_cancel,
    #                 ),
    #                 ft.TextButton(
    #                     content="Clear All",
    #                     on_click=handle_clear,
    #                 ),
    #             ],
    #         ),
    #         padding=ft.Padding(top=0, bottom=20, left=20, right=20),
    #         width=400,
    #     )

    #     BottomSheet = ft.BottomSheet(
    #         # scrollable=True,
    #         bgcolor=DraculaColors.CURRENT_LINE,
    #         content=ft.Column(
    #             controls=[
    #                 sc,
    #                 savebut,
    #             ],
    #             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    #             tight=True,
    #         ),
    #         on_dismiss=lambda _, data=items: self.handle_dismiss_save(data),
    #     )
    #     self.page.show_dialog(BottomSheet)

    #     await ft.SharedPreferences().set("save_data_list", json.dumps(saved_data))
    #     await self.initialize_data()

    # async def select_dir(self):
    #     stored_dir = await ft.SharedPreferences().get("user_dir")
    #     if stored_dir:
    #         self.user_dir = stored_dir
    #         return self.user_dir

    #     if not self.page.web:
    #         picked_dir = await ft.FilePicker().get_directory_path(
    #             dialog_title="Please select a directory?"
    #         )
    #         if picked_dir:
    #             await ft.SharedPreferences().set("user_dir", picked_dir)
    #             self.user_dir = picked_dir
    #             return self.user_dir
    #     return self.user_dir

    # async def save_screenshot(self, screenshot: ft.Screenshot, path, genid=""):
    #     image = await screenshot.capture()
    #     print(f"image data size: {len(image)} bytes")

    #     obj_path = os.path.join(path, f"jackpot_{genid}.png")
    #     print(f"saving screenshot to: {obj_path}")
    #     with open(obj_path, "wb") as f:
    #         f.write(image)

    # def handle_dismiss_save(self, data: list):
    #     self.page.run_task(self.dismiss_save_data, data)

    # async def dismiss_save_data(self, data: list):
    #     raw_json = await ft.SharedPreferences().get("save_data_list")
    #     saved_data = json.loads(raw_json) if raw_json else []
    #     saved_data.extend(data)
    #     await ft.SharedPreferences().set("save_data_list", json.dumps(saved_data))
    #     self.page.run_task(self.initialize_data)
    #     # print(f'dismiss_save_data {saved_data=}')
    #     self.Badge_number(len(saved_data))

    # async def initialize_data(self):
    #     """异步加载初始数据并渲染"""
    #     try:  # 确保这是一个异步函数
    #         raw_json = await ft.SharedPreferences().get("save_data_list")
    #         saved_data = json.loads(raw_json) if raw_json else []
    #         initial_count = len(saved_data)
    #         self.lottery_icon.badge.label = f"{initial_count}"
    #         if self.lottery_icon.badge.label == "0":
    #             self.lottery_icon.badge.label_visible = False
    #         else:
    #             self.lottery_icon.badge.label_visible = True

    #     except Exception as e:
    #         print(f"Waiting for interface initialization...: {e}")
    #     finally:
    #         self.Fab.update()

    # def Badge_number(self, lens: int = 0):
    #     self.page.run_task(self.initialize_data)
    #     for nbar in self.page.navigation_bar.destinations:
    #         if isinstance(nbar, ft.NavigationBarDestination) and nbar.label == "Lotter":
    #             if lens != 0:
    #                 nbar.icon.badge = str(lens)
    #             else:
    #                 nbar.icon.badge = None
    #     self.page.update()

    # def set_Lotter_buttons(self):
    #     Lottery_item_count_data = {"2": 2, "5": 5, "10": 10, "15": 15}
    #     button_list = []
    #     for key, item in Lottery_item_count_data.items():
    #         button_list.append(
    #             ft.Button(
    #                 f"{key} items",
    #                 tooltip=ft.Tooltip(
    #                     message=f"Set the number of lottery tickets to obtain to {key}."
    #                 ),
    #                 # 【重要】使用默认参数 data=item 来破解 Lambda 闭包陷阱
    #                 on_click=lambda e, data=item: self.save_Lottery_item(data),
    #             )
    #         )

    #     return button_list

    # def save_Lottery_item(self, data: int):
    #     self.page.session.store.set("Lottery_item_count", data)
    #     self.page.show_dialog(get_snack_bar(f"setting item count {data}"))

    # def Get_Lottery_data(self, index: int):
    #     print(f"Get_Lottery_data is runing {index=}")
    #     try:
    #         settings = self.page.session.store.get("settings")
    #         filters = self.page.session.store.get("filters")
    #         lic = self.page.session.store.get("Lottery_item_count") or 5
    #         for isdism in self.lottery_items_column.controls:
    #             if not isdism:
    #                 continue
    #             if isinstance(isdism, dism):
    #                 if isdism.is_refreshing:
    #                     self.page.show_dialog(
    #                         get_snack_bar(
    #                             "The DISM tasks were not all completed.", "error"
    #                         )
    #                     )
    #                     return

    #         self.lottery_items_column.controls.clear()
    #         for _ in range(lic):
    #             # listext = listext_onlong()
    #             listext = dism()
    #             listext.setting_args(settings["randomData"], filters, self.Badge_number)
    #             self.lottery_items_column.controls.append(listext)
    #         # self.lottery_items_column.cilcked(settings["randomData"], filters=filters)
    #     except Exception as e:
    #         self.page.show_dialog(
    #             get_snack_bar("Failed to retrieve settings data.", "error")
    #         )

    def get_data_view(self):
        return ft.Column(
            controls=[
                ft.Image(
                    src="lotter.png",
                    fit=ft.BoxFit.FIT_HEIGHT,
                    width=288 * 0.45,
                    height=131 * 0.45,
                ),
                ft.Divider(),
                self.itemslist,
                self.serendipitous_Capture,
                self.comandlist,
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
