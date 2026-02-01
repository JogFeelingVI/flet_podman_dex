# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-01 04:45:08


from .jackpot_core import randomData, filter_for_pabc
from .SnackBar import get_snack_bar
from .DraculaTheme import DraculaColors
from .loger import logr
import flet as ft
import datetime
import os
import asyncio

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


# region serendipitousCapture
class serendipitousCapture(ft.Card):
    """创建一个控件 用来使用列表拍照"""

    def __init__(self):
        super().__init__()
        self.get_exp_all = None
        self.scshot = self.__build_exp()
        self.tips = self.__build_tips()
        self.content = self.__build__Container()
        self.visible = False
        self.savePng = ft.FilePicker()

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

            # 4. 【非常重要】截图控件必须先添加到页面上
            # 我们把它放到 overlay 中，这样它就存在于页面树中，但不会破坏现有布局
            image = await self.scshot.capture()
            stored_id = await ft.SharedPreferences().get("stored_id")
            id = os.path.splitext(os.path.basename(stored_id))[0]
            png_name = f"{id}.png"
            # png_path =  os.path.join(app_temp_path, png_name)
            save_png = await self.savePng.save_file(
                dialog_title=f"Save as {png_name} file.",
                allowed_extensions=["png"],
                file_name=png_name,
                src_bytes=image,
            )
            if save_png:
                with open(save_png, "wb") as f:
                    f.write(image)
            await self.update_tips(f"Storage file directory {png_name}.")
            await self.update_tips(f"Storage task completed.")

        except Exception as er:
            logr.info(f"Capture error.", er)
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


# endregion


# region ItemC2
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
            shape=ft.RoundedRectangleBorder(
                side=ft.BorderSide(width=1, color=DraculaColors.CURRENT_LINE), radius=8
            ),
            # bgcolor=DraculaColors.CURRENT_LINE,  # 替换为你的 DraculaColors.CURRENT_LINE
            selected_color=ft.Colors.TRANSPARENT,
            check_color=DraculaColors.ORANGE,
            delete_icon_color=DraculaColors.RED,
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
        # logr.info(f"markdata is running. {name}")
        self.page.run_task(self.SearchForData, name)

    async def SearchForData(self, name: str):
        logr.info(f"SearchForData {name}")
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
                    logr.info("Search successful")
                    break  # 成功后直接跳出循环
                else:
                    # 失败但未达到上限，更新 UI 并稍作等待
                    self.chip_content.value = tempd
                    self.chip_content.color = DraculaColors.ORANGE
                    self.state_exp = "ref"
                    self.update()
                    await asyncio.sleep(0.3)  # 给 CPU 喘息时间，也让 UI 有机会渲染
                count += 1
                if count >= max_retries:
                    logr.info("count is max_retries, work stoping.")
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
        logr.info("向右滑动：正在刷新数据...")
        self.refresh(name="refresh_data")

    def save_item(self):
        """左滑逻辑：保存项目"""
        logr.info("向左滑动：项目已保存")
        # 这里执行你的保存逻辑
        self.page.show_dialog(ft.SnackBar(ft.Text("项目已保存！")))

    async def handle_select(self, e):
        if self.is_refreshing:
            self.chip.selected = False
            return
        if self.state_exp != "done":
            self.chip.selected = False
            return
        self.chip.shape = ft.RoundedRectangleBorder(
            side=ft.BorderSide(
                width=1,
                color=DraculaColors.ORANGE
                if self.chip.selected
                else DraculaColors.CURRENT_LINE,
            ),
            radius=8,
        )

        self.update()

    def handle_delete(self, e):
        if self.is_refreshing or self.chip.selected:
            return
        if self.Itemc2_remove:
            self.Itemc2_remove(self)
        self.chip.update()
        logr.info("点击了删除图标")


# endregion


# region itemsList
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
            logr.info(f"add_item type {type(control)}")
            return
        itemc2_len = [x for x in control.controls if isinstance(x, ItemC2)].__len__()
        if itemc2_len < self.max_item:
            temp = ItemC2()
            temp.setting_Itemc2_Remove(itemc2remove)
            control.controls.append(temp)
            logr.info("Add ItemC2")
            self.update()

    def all_refresh(self):
        """全部刷新"""
        control = self.content.content
        if not isinstance(control, ft.Column):
            logr.info(f"all_refresh {type(control)}")
            return
        itemc2_all = [x for x in control.controls if isinstance(x, ItemC2)]
        for item in itemc2_all:
            if item.chip.selected == False:
                item.refresh(name="all_refresh")

    def get_item_exp(self):
        """"""
        control = self.content.content
        if not isinstance(control, ft.Column):
            logr.info(f"all_refresh {type(control)}")
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


# endregion


# region commandList
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
                    key="add_close",
                    icon=ft.Icons.INSERT_EMOTICON,
                    content="Add",
                    on_click=self.handle_add,
                ),
                ft.TextButton(
                    icon=ft.Icons.REFRESH,
                    content="Refresh",
                    on_click=self.handle_refresh,
                ),
                ft.TextButton(
                    icon=ft.Icons.SAVE_AS,
                    content="Export",
                    on_click=self.handle_export,
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
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


# endregion


# region LotteryPage
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

    # region get_data_view
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

    # endregion


# endregion
