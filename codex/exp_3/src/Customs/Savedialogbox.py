# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-02 09:10:57
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-21 00:05:38


import asyncio

# import datetime
from calendar import c
import io
import multiprocessing
import os
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass, field

import flet as ft
from PIL import Image, ImageChops, ImageFont

from .adbox import adbx
from .asyncredis import RedisAPI
from .byterfiles import BinaryConverter as bc
from .DraculaTheme import DraculaColors, HarmonyColors, RandColor
from .jackpot_core import calculate_batch_wrapper, filter_for_pabc, randomData
from .LotteryRendering import Rendering
from .svgbase64 import svgimage
from .env_manager import env_manager

# tracemalloc.start()


# region _savedialog
class savedialog:
    def __init__(self):
        self.conten = self.__builde_conter()
        self.adb = adbx(None, self.conten, Child_padding=0)
        self.adb.setting_did_mount_callback(self.load_exp)
        self.exps_is_build = True
        self.getallexp = None
        self.all_exp = None
        self.cancel_callback = None

    def seting_get_all_exp(self, getallexp=None):
        self.getallexp = getallexp

    def setting_cancel(self, cancel_callback=None):
        self.cancel_callback = cancel_callback

    def __builde_conter(self):
        title_color = DraculaColors.ORANGE
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.genid = randomData.generate_secure_string(8)
        footer = ft.Row(
            controls=[
                ft.Text(
                    f"{now} {self.genid}",
                    size=14,
                    font_family="Inter_18pt-SemiBold",
                    color=ft.Colors.with_opacity(0.7, DraculaColors.ORANGE),
                )
            ],
            alignment=ft.MainAxisAlignment.END,
        )
        title = ft.Text(
            "Jackpot Lotter",
            size=28,
            weight="bold",
            font_family="RacingSansOne-Regular",
            color=title_color,
            italic=True,
        )

        self.exps = ft.Column(
            tight=True,
            width=float("inf"),
            spacing=5,
        )
        acts = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.Button(
                    expand=2,
                    icon=ft.Icons.CANCEL,
                    bgcolor=ft.Colors.TRANSPARENT,
                    color=DraculaColors.FOREGROUND,
                    content="Cancel",
                    on_click=self.__handle_cancel,
                ),
                ft.Button(
                    expand=3,
                    icon=ft.Icons.IMAGE,
                    bgcolor=DraculaColors.RED,
                    color=DraculaColors.FOREGROUND,
                    content="Save to png",
                    on_click=self.__handle_save,
                ),
            ],
        )

        conter = ft.Container(
            width=float("inf"),
            padding=5,
            border_radius=10,
            bgcolor=DraculaColors.BACKGROUND,
            content=ft.Column(
                tight=True,
                spacing=5,
                controls=[
                    title,
                    self.exps,
                    footer,
                    acts,
                ],
            ),
        )
        self.Screenshot = ft.Screenshot(
            content=conter,
        )
        content = ft.Column(
            controls=[self.Screenshot],
            tight=True,
            # on_size_change=self.handle_resize,
        )
        return content

    async def load_exp(self):
        self.exps_is_build = False
        if not self.getallexp:
            # print("not is getallexp func.")
            return
        self.all_exp = self.getallexp()
        if len(self.all_exp) == 0:
            # print("len all_exp is zero.")
            return
        items = []
        for i, _exp in enumerate(self.all_exp):
            items.append(self.CreateItem(_exp, i, 18))
            if (i + 1) % 5 == 0 and (i + 1) < len(_exp):
                items.append(self.CreateItem("", -1))
        self.exps.controls = items
        self.exps.update()
        self.exps_is_build = True

    def __handle_cancel(self):
        if self.adb.running:
            if self.cancel_callback:
                self.cancel_callback(self.all_exp)
            self.adb.page.pop_dialog()

    def CreateItem(self, text: str = "", i: int = 0, fontsize: int = 18):
        userColor = RandColor(mode="neon")
        twidth = 388 - 47
        if self.adb.page.platform.is_mobile():
            twidth = 292 - 47
        sizes = caclfsize(text=text, defsize=fontsize, targetwidth=twidth)
        item = (
            ft.Container(
                padding=ft.Padding.all(6),
                width=float("inf"),  # 388
                bgcolor=ft.Colors.with_opacity(0.1, userColor),
                border_radius=5,
                border=ft.Border.only(left=ft.BorderSide(3, color=RandColor())),
                # on_size_change=onresize,
                content=ft.Stack(
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    controls=[
                        ft.Text(
                            f"{text}",
                            size=sizes,
                            text_align=ft.TextAlign.START,
                            weight=ft.FontWeight.BOLD,
                            color=userColor,
                            font_family="Inter_18pt-SemiBold",
                        ),
                        ft.Image(
                            src=svgimage(i + 1),
                            width=fontsize * 1.68,
                            height=fontsize * 1.68,
                            color=ft.Colors.with_opacity(0.7, RandColor()),
                            right=-7,
                            bottom=-7,
                        ),
                    ],
                ),
            )
            if i >= 0
            else ft.Container(padding=5, height=10)
        )
        return item

    async def __handle_save(self):
        if self.exps_is_build:
            is_mobile_or_web = self.adb.page.web or self.adb.page.platform in [
                ft.PagePlatform.ANDROID,
                ft.PagePlatform.IOS,
            ]
            try:
                image = await self.Screenshot.capture()
                image = self.crop_solid_bg(image)
                png_name = f"{self.genid}.png"

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
                print(f"Storage task completed.")
            except Exception as er:
                print(f"Image saving error. {er}")
            finally:
                await asyncio.sleep(1)
                self.adb.page.pop_dialog()

    def crop_solid_bg(self, image_bytes):
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # 2. 获取图片左上角 (0,0) 的像素颜色，假设这就是背景色
        # 如果你确定背景是白色，也可以直接写 bg_color = (255, 255, 255)
        bg_color = img.getpixel((img.width - 1, img.height - 1))
        # 3. 创建一张全背景色的假图片
        bg_img = Image.new("RGB", img.size, bg_color)
        # 4. 求差集，找到所有不是背景颜色的像素
        diff = ImageChops.difference(img, bg_img)
        # 5. 稍微模糊一下，处理边缘的抗锯齿毛边，并增强对比度
        diff = diff.convert("L").point(lambda x: 255 if x > 30 else 0)
        # 6. 获取所有非背景区域的边界
        bbox = diff.getbbox()
        if bbox:
            byte_stream = io.BytesIO()
            img.crop(bbox).save(byte_stream, format="PNG")
            # print(f"crop png -> {bbox}")
            return byte_stream.getvalue()
        return image_bytes


# endregion


# region _tadbx
@dataclass
class TaskState:
    result: list = field(default_factory=list)
    max_value: int = 100
    min_value: int = 0
    jdu: float = 0.0
    info: str = ""
    task: str = "none"

    def addinfo(self, text: str) -> str:
        self.info = f"{text}"

    def getinfo(self) -> str:
        info = self.info
        self.info = None
        return info

    def additem(self, item):
        self.result.append(item)
        temp = [item[-1] for item in self.result]
        self.max_value = max(temp)
        self.min_value = min(temp)

    def getitems(self, sord: bool = False):
        if not sord:
            return self.result[-10:]
        else:
            temp = list(sorted(self.result, key=lambda x: x[-1]))
            return temp


class tadbx:
    def __init__(self):
        self.conten = self.__builde_conter()
        self.adb = adbx(None, self.conten)
        self.detectstatus = TaskState()

    def __handle_Close(self, e):
        if self.adb.running and self.detectstatus.task == "none":
            self.adb.page.pop_dialog()

    def __handle_start(self, e):
        if self.adb.running and self.detectstatus.task == "none":
            self.detectstatus.task = "Detection"
            # 旧版采用异步更新放
            # self.adb.page.run_task(self.Detection)
            # self.adb.page.run_task(self.showresult)
            # 新版采用callbakc的方法
            self.adb.page.run_task(self.Detection_Filter_callback)

    async def Detection_Filter_callback(self):
        """采用callback 实时驱动界面"""
        adb_page = self.adb.page

        def update_callback():
            if (text := self.detectstatus.getinfo()) is not None:
                self.info_display.controls[0].value = text
            self.smax.content.value = self.detectstatus.max_value
            self.smin.content.value = self.detectstatus.min_value
            self.pbar.value = self.detectstatus.jdu
            self.tips.value = (
                f"Testing in progress... {self.pbar.value * 100:.0f}% complete"
            )
            self.adb.content.update()
            if self.detectstatus.task in ["pass_rate_zero", "skip", "error"]:
                self.detectstatus.task = "none"

        def safe_callback():
            # 使用 page.run_threadsafe 或者简单的 loop.call_soon_threadsafe
            # 在 Flet 中，直接修改值并 update 也是可以的，但更严谨的做法是：
            adb_page.loop.call_soon_threadsafe(update_callback)
            time.sleep(0.1)  # 模拟一些处理时间，实际中可以根据需要调整或去掉

        try:
            await asyncio.to_thread(self.Detection_Filter, safe_callback)
            await asyncio.sleep(0.5)
        except Exception as er:
            self.detectstatus.task = "error"
            print(f"Detection_Filter_callback error. {er}")
        finally:
            self.detectstatus.task = "none"
            adb_page.update()
            await self.update_more_list()

    def Detection_Filter(self, callback):
        self.detectstatus.task = "Detection"
        settings = self.adb.page.session.store.get("settings")
        filters = self.adb.page.session.store.get("filters")
        settings = bc.from_base64(settings)
        filters = bc.from_base64(filters)

        self.detectstatus.addinfo("Load settings & filters data.")
        callback()

        if not filters or not settings:
            self.detectstatus.addinfo("If filters/settings is empty.")
            # await asyncio.sleep(0.3)
            self.detectstatus.task = "skip"
            callback()
            return

        results = []
        _rdpn = randomData(seting=settings["randomData"])
        for _ in range(1000):
            results.append(_rdpn.get_pabc())
        self.detectstatus.addinfo(f"Create a data pool, {len(results)}.")
        callback()
        print("start test filters...")
        for i, _fitem in enumerate(filters):
            try:
                _f2func = filter_for_pabc(filters=[_fitem])
                pass_rate = (
                    sum([1 for r in results if _f2func.handle(r)]) / len(results) * 100
                )
            except Exception as er:
                self.detectstatus.addinfo(f"⚠️ {_fitem['condition']} Syntax error.")
                self.detectstatus.task = "error"
                callback()
                return
            prinfo = [
                f"{_fitem['func']}",
                f"{_fitem['target']}",
                f"{_fitem['condition']}",
                int(pass_rate),
            ]
            self.detectstatus.jdu = (i + 1) / len(filters)
            self.detectstatus.additem(prinfo)
            self.detectstatus.addinfo(
                f"{_fitem['func']} {_fitem['target']} {_fitem['condition']}"
            )
            callback()
            if pass_rate < 1.0:
                self.detectstatus.addinfo(f"⚠️ {_fitem['condition']} Logical error.")
                self.detectstatus.task = "pass_rate_zero"
                callback()
                return
        self.detectstatus.addinfo("🍻 Test complete.")
        self.detectstatus.task = "done"
        callback()

    def __builde_conter(self):
        title = ft.Row(
            spacing=3,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SETTINGS_ACCESSIBILITY, size=18),
                ft.Text(
                    "Filter Testing Dashboard",
                    size=18,
                    weight="bold",
                    color=DraculaColors.FOREGROUND,
                ),
            ],
        )
        maxmin = ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                _smax := ft.Container(
                    expand=1,
                    height=65,
                    # 1. 删除 padding=10，避免上下空间被挤压
                    # 2. 加上 alignment，让内部文字完美水平+垂直居中
                    alignment=ft.Alignment.CENTER,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(
                        0.1, RandColor(mode="neon", hue="green")
                    ),
                    border=ft.Border.all(
                        1,
                        ft.Colors.with_opacity(
                            0.2, RandColor(mode="neon", hue="green")
                        ),
                    ),
                    content=ft.Text(
                        "78",
                        size=40,
                        color=ft.Colors.with_opacity(
                            0.8, RandColor(mode="neon", hue="green")
                        ),
                        # text_align="center" # 其实加了 alignment 后，这个可以不写了
                    ),
                ),
                _smin := ft.Container(
                    expand=1,
                    height=65,
                    alignment=ft.Alignment.CENTER,  # 同上，完美居中
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(
                        0.1, RandColor(mode="neon", hue="red")
                    ),
                    border=ft.Border.all(
                        1,
                        ft.Colors.with_opacity(0.2, RandColor(mode="neon", hue="red")),
                    ),
                    content=ft.Text(
                        "23",
                        size=40,
                        color=ft.Colors.with_opacity(
                            0.8, RandColor(mode="neon", hue="red")
                        ),
                    ),
                ),
            ],
        )
        self.smax = _smax
        self.smin = _smin
        schedule = ft.Column(
            tight=True,
            spacing=5,
            controls=[
                tips := ft.Text(
                    "Testing in progress...84% complete",
                    size=15,
                    weight="bold",
                    color=RandColor(mode="neon", hue="blue"),
                    text_align=ft.TextAlign.END,
                ),
                pbar := ft.ProgressBar(
                    value=0.5,
                    expand=1,
                    height=10,
                    color=RandColor(mode="neon"),
                    border_radius=5,
                ),
            ],
        )
        self.tips = tips
        self.pbar = pbar
        self.info_display = ft.Column(
            tight=True,
            spacing=3,
            scroll=ft.ScrollMode.HIDDEN,
            controls=[
                ft.Text(
                    "Click the `Start testing` to begin the test.",
                    italic=True,
                    color=ft.Colors.with_opacity(0.7, "#bebebe"),
                ),
            ],
        )
        # def handle_more_on_siee(e):
        #     print(f"more e: {e}")
        self.more_butter = ft.Row(
            spacing=5,
            controls=[
                ft.Container(
                    padding=0,
                    expand=True,
                    height=1,
                    bgcolor=DraculaColors.FOREGROUND,
                ),
                ft.Container(
                    padding=0,
                    content=ft.Text("MORE"),
                    on_click=self.handle_more,
                ),
            ],
        )
        self.more_display = ft.Column(
            data="hide",  # hide or show
            tight=True,
            spacing=0,
            height=160,
            visible=False,
            scroll=ft.ScrollMode.HIDDEN,
            controls=[self.Details(type="tips", text="Waiting for the test to end.")],
            # on_size_change=handle_more_on_siee
        )
        acts = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.TextButton(
                    "Close",
                    expand=1,
                    on_click=self.__handle_Close,
                    style=ft.ButtonStyle(color="#dfdfdf"),
                ),
                # 确定按钮用红色突出显示危险操作
                ft.Button(
                    "Start testing",
                    expand=3,
                    color=DraculaColors.FOREGROUND,
                    bgcolor=DraculaColors.RED,
                    on_click=self.__handle_start,
                ),
            ],
        )
        conter = ft.Container(
            # width=400,
            padding=5,
            border_radius=0,
            content=ft.Column(
                tight=True,
                spacing=5,
                controls=[
                    title,
                    maxmin,
                    schedule,
                    self.more_butter,
                    self.more_display,
                    self.info_display,
                    acts,
                ],
            ),
        )
        return conter

    async def handle_more(self, e):
        self.more_display.visible = not self.more_display.visible
        self.more_display.update()

    async def update_more_list(self):
        items = self.detectstatus.getitems(sord=True)
        if not items:
            return
        newitems = []
        for item in items[:10]:
            newitems.append(self.Details(*item, type="info"))
        self.more_display.controls = newitems

    def Details(self, *args, **kwargs):
        # bold = kwargs.get("bold", False)
        # size = kwargs.get("size", 14)
        typed = kwargs.get("type", "more")  # more info
        text = kwargs.get("text", "---")
        # usercolor = kwargs.get("usercolor", RandColor(mode="neon"))
        match typed:
            case "tips":
                temp = ft.Container(
                    data="tips",
                    padding=0,
                    content=ft.Row(
                        spacing=5,
                        controls=[
                            ft.Container(
                                padding=0, content=ft.Icon(ft.Icons.TIPS_AND_UPDATES)
                            ),
                            ft.Container(
                                padding=0,
                                content=ft.Text(text),
                                on_click=self.handle_more,
                            ),
                        ],
                    ),
                )
            case "info":
                f, t, c, pr = args
                pr = f"{pr}%"
                # print(f'{args}')
                temp = ft.Container(
                    data="info",
                    padding=2,
                    content=ft.Row(
                        spacing=3,
                        controls=[
                            ft.Text(
                                f"{pr:<5}", weight="bold", color=RandColor(hue="red")
                            ),
                            ft.Text(f"{f}", color=RandColor(hue="blue")),
                            ft.Text(
                                f"{t:<2}", weight="bold", color=RandColor(hue="yellow")
                            ),
                            ft.Text(f"{c}", color=RandColor(hue="green")),
                        ],
                    ),
                )
            case _:
                pass
        return temp


# endregion


# region upstash token


class upstashtoken:
    def __init__(self):
        self.conten = self.__builde_conter()
        self.adb = adbx(None, self.conten)
        self.detectstatus = TaskState()
        self.valid_data = None

    def __builde_conter(self):
        title = ft.Column(
            tight=True,
            width=float("inf"),
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Configuration", size=18, color=DraculaColors.FOREGROUND),
                ft.Text(
                    "Adjust your preferences below",
                    size=13,
                    color=ft.Colors.with_opacity(0.4, DraculaColors.FOREGROUND),
                ),
            ],
        )
        # 显示token 输入窗口
        apitoken = ft.Column(
            tight=True,
            width=float("inf"),
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Text(
                    "API Token".upper(),
                    size=13,
                    color=ft.Colors.with_opacity(0.4, DraculaColors.FOREGROUND),
                ),
                intoken := ft.TextField(
                    hint_text="Enter your token",
                    border=ft.InputBorder.NONE,
                    cursor_height=15,
                    text_size=15,
                    dense=True,
                    content_padding=ft.Padding.all(0),
                ),
                intoken_url := ft.TextField(
                    hint_text="https://******.upstash.io",
                    border=ft.InputBorder.NONE,
                    cursor_height=15,
                    text_size=15,
                    dense=True,
                    content_padding=ft.Padding.all(0),
                ),
                intoken_tip := ft.Text(
                    "Securely sync your project data using your unique access key.",
                    no_wrap=False,
                    max_lines=2,
                    size=12,
                    color=ft.Colors.with_opacity(0.4, DraculaColors.FOREGROUND),
                ),
            ],
        )
        self.intoken = intoken
        self.intoken_tip = intoken_tip
        self.intoken_url = intoken_url
        asyncset = ft.Column(
            tight=True,
            width=float("inf"),
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Text(
                    "Settings".upper(),
                    size=13,
                    color=ft.Colors.with_opacity(0.4, DraculaColors.FOREGROUND),
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Sync Data",
                            size=15,
                            color=ft.Colors.with_opacity(1, DraculaColors.FOREGROUND),
                        ),
                        switch := CustomSwitch(value=False),
                    ]
                ),
            ],
        )
        self.syncsw = switch
        # 取消 按钮牛
        acts = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.TextButton(
                    "Cancel",
                    on_click=self.handle_cancel,
                    style=ft.ButtonStyle(
                        color=ft.Colors.with_opacity(0.8, DraculaColors.FOREGROUND)
                    ),
                ),
                # 确定按钮用红色突出显示危险操作
                ft.TextButton(
                    "Apply",
                    on_click=self.handle_apply,
                    style=ft.ButtonStyle(color=RandColor(hue="blue")),
                ),
            ],
        )
        conter = ft.Container(
            # width=400,
            padding=5,
            border_radius=0,
            content=ft.Column(
                tight=True,
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    title,
                    apitoken,
                    ft.Divider(color=DraculaColors.FOREGROUND),
                    asyncset,
                    acts,
                ],
            ),
        )
        return conter

    def setting_apply_callback(self, callblack):
        self.applycallback = callblack

    def setting_valid_info(self, data: dict):
        if data:
            self.intoken.value = data["token"]
            self.intoken_url.value = data["api"]
            self.syncsw.value = data["sync"]
            self.valid_data = data
            self.adb.update()

    def handle_cancel(self):
        self.adb.page.pop_dialog()

    async def handle_apply(self):
        # 1. 提取 UI 更新辅助函数，消除重复的冗余代码
        async def show_tip(msg: str, color: str):
            self.intoken_tip.value = msg
            self.intoken_tip.color = ft.Colors.with_opacity(1, color)
            self.intoken_tip.update()  # 先更新 UI 给用户看
            await asyncio.sleep(0.5)  # 再稍微停留一下

        # 获取并清理输入（去除首尾空格）
        token = self.intoken.value.strip()
        token_url = self.intoken_url.value.strip()

        # 2. 基础输入校验
        if not token:
            await show_tip("Please enter the upstash token.", DraculaColors.RED)
            return

        if not token_url:
            await show_tip(
                "Please enter upstash to retrieve the URL.", DraculaColors.RED
            )
            return

        # 修复 Bug：正确补全 HTTPS
        if not token_url.startswith(("http://", "https://")):
            token_url = f"https://{token_url}"

        # 3. 缓存检测（如果信息没变且之前验证过，直接生效并退出）
        # 使用 dict.get 更加安全，防止 KeyError
        # if (
        #     self.valid_data
        #     and self.valid_data.get("status") == "valid"
        #     and self.valid_data.get("token") == token
        #     and self.valid_data.get("api") == token_url
        # ):
        #     self.valid_data["sync"] = self.syncsw.value
        #     if self.applycallback:
        #         self.adb.page.run_task(self.applycallback, self.valid_data)
        #     self.adb.page.pop_dialog()
        #     return

        # 4. 开始 API 测试流程
        await show_tip("Connecting to Upstash...", DraculaColors.YELLOW)

        redisapi = RedisAPI(url=token_url, token=token)
        test_token = "abc_123_xyz"
        user_id = "user_999"

        try:
            # 第一步：尝试写入数据
            save_success = await redisapi.save_token(
                test_token, user_id, expire_seconds=30
            )
            if not save_success:
                await show_tip("Connection failed. Check URL/Token.", DraculaColors.RED)
                return

            # 第二步：尝试读取数据并验证
            await show_tip("Verifying saved data...", DraculaColors.GREEN)
            result = await redisapi.verify_token(test_token)

            # 5. 最终结果处理
            if result.get("is_valid"):
                # 验证成功
                await show_tip("Token verified successfully!", DraculaColors.GREEN)

                if self.applycallback:
                    backdata = {
                        # new data
                        "token": token,
                        "api": token_url,
                        "sync": self.syncsw.value,
                        "status": "valid",
                        "message": "token is valid and data saved successfully.",
                        "updated_at": int(time.time()),
                        "note": f"User updated token settings at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}",
                    }
                    # print(f'backdata: {backdata}')
                    await self.applycallback(backdata)

                self.adb.page.pop_dialog()
                return  # 修复 Bug：验证成功后必须 return，防止穿透到下面

            else:
                # 验证失败
                await show_tip("Token verification failed.", DraculaColors.RED)

        except Exception as e:
            # 捕获网络异常等未预期错误
            await show_tip(f"Error: {str(e)[:20]}", DraculaColors.RED)


# endregion


# region Custom_Switch
class CustomSwitch(ft.Container):
    def __init__(self, value: bool = False, on_change=None):
        super().__init__()
        self._load_colors()

        # --- 容器基础属性 ---
        self.width = 35
        self.height = 20
        self.padding = 3
        self.border_radius = self.height / 2
        self.border = ft.Border.all(1, self.border_color)
        # 修正：使用 Flet 标准动画枚举
        self.animate = ft.Animation(400, ft.AnimationCurve.DECELERATE)
        self.on_click = self._toggle_switch

        # --- 状态与回调 ---
        self._value = value
        self.on_change = on_change

        # --- 构建内部滑块 ---
        self.content = self._build_handle()

        # --- 强制同步初始 UI 与初始状态 ---
        self._update_ui_state(self._value)

    # 💡 优化 1：使用 property，可以用 switch.value = True 直接赋值
    @property
    def value(self) -> bool:
        return self._value

    @value.setter
    def value(self, new_value: bool):
        self._value = new_value
        self._update_ui_state(new_value)
        # 💡 优化 2：安全更新，防止在 Mount 前调用导致报错
        if self.page:
            self.update()

    def setingbadge(self, value: int):
        if value is None or value == -1:
            self.badge = None
        else:
            self.badge = f"{value}"
        if self.page:
            self.update()

    def _update_ui_state(self, is_active: bool):
        """内部方法：根据当前布尔值更新 UI 样式"""
        # ⚠️ 注意：这里保留了你原本的逻辑 (True在左侧，False在右侧)
        # 如果你想改成常规的 (True在右边开启)，请把下面 True 和 False 的代码互换
        if is_active:
            self.bgcolor = ft.Colors.with_opacity(0.3, self.active_color)
            self.alignment = ft.Alignment.CENTER_RIGHT
            self.handle.bgcolor = self.default_color
        else:
            self.bgcolor = ft.Colors.with_opacity(0.3, self.default_color)
            self.alignment = ft.Alignment.CENTER_LEFT
            self.handle.bgcolor = self.active_color

    def _load_colors(self):
        """加载颜色 (修复了拼写)"""
        self.active_color = RandColor(hue="red")
        self.default_color, self.border_color = HarmonyColors(
            base_hex_color=self.active_color, harmony_type="triadic"
        )

    def _build_handle(self):
        self.handle = ft.Container(
            height=12,
            width=12,
            border_radius=6,
            bgcolor=self.active_color,
            border=ft.Border.all(1, self.border_color),
            # 💡 优化 3：给内部滑块也加上动画，颜色过渡会非常柔和
            animate=ft.Animation(400, ft.AnimationCurve.DECELERATE),
        )
        return self.handle

    def _toggle_switch(self, e):
        # 切换状态，自动触发 @value.setter 里的 UI 更新逻辑
        self.value = not self.value

        # 触发外部传入的回调函数
        if self.on_change:
            self.on_change(self)


# endregion


# region CasfontW
def caclfsize(
    text: str,
    fontname: str = None,
    targetwidth: int = 355,
    defsize: int = 18,
    maxsize: int = 26,
) -> int:
    """
    根据目标像素宽度计算最佳字体大小
    :param fontpath: .ttf 字体文件的物理路径
    :param text: 要显示的文本内容
    :param targetwidth: 目标的像素宽度 (默认 360)
    :param defsize: 默认大小、起始大小
    :param maxsize: 最大值
    :return: 建议的 font_size (int)
    """
    low = 1
    high = maxsize  # 设置一个合理的上限
    best_size = defsize

    if not fontname:
        fontname = "Inter_18pt-SemiBold"

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    # 向上跳一级到 /src/，再进入 assets/fonts/
    FONT_PHYSICAL_PATH = os.path.abspath(
        os.path.join(CURRENT_DIR, "..", "assets", "fonts", f"{fontname}.ttf")
    )

    # 使用二分法快速逼近目标宽度
    while low <= high:
        mid = (low + high) // 2
        try:
            font = ImageFont.truetype(FONT_PHYSICAL_PATH, mid)
            # 获取文本渲染后的边界框 [left, top, right, bottom]
            bbox = font.getbbox(text)
            current_width = bbox[2] - bbox[0]

            if current_width <= targetwidth:
                best_size = mid
                low = mid + 1
            else:
                high = mid - 1
        except Exception:
            # print(f'caclfsize error, use defsize {defsize}: {ex}')
            return defsize
    return max(defsize, best_size)


# ednregion


# region joblibdlg
class joblibdlg:
    def __init__(self):
        self.conten = self.__builde_conter()
        self.adb = adbx(None, self.conten)
        self.taskbar_value = 0
        self.is_computing = False
        self.valid_results = []
        self.Launch_Cancelled = "none"  # none launch

    async def handle_cancel(self):
        if self.is_computing:
            self.Launch_Cancelled = "launch"
            while self.Launch_Cancelled == "launch":
                await asyncio.sleep(1)
            return
        self.adb.page.pop_dialog()

    def setting_add_remove(self, add=None, remove=None):
        self.additem = add
        self.removeitem = remove

    async def handle_start(self):
        if self.is_computing:
            return
        self.is_computing = True
        settings = self.adb.page.session.store.get("settings")
        filters = self.adb.page.session.store.get("filters")

        settings = bc.from_base64(settings)
        filters = bc.from_base64(filters)
        if not settings:
            return
        if not filters:
            filters = []

        def safe_get_int(control, default):
            val = control.value
            if val and str(val).strip():  # 确保有值且不是纯空格
                try:
                    return int(val)
                except ValueError:
                    print(
                        f"Warning: Enter' {val} 'Not a valid number, use default value {default}"
                    )
            return default

        timeout_limit = safe_get_int(self.intimeout, 60)
        target_quantity = safe_get_int(self.intargetquantity, 0)
        max_time = safe_get_int(self.inmaxtime, 5)
        self.valid_results = []
        try:
            # 逻辑微调
            if timeout_limit == 0 and target_quantity == 0:
                timeout_limit = 60

            max_time = max_time if max_time < 60 else 60

            if timeout_limit == 0 and target_quantity >= 1:
                timeout_limit = 60 * max_time

            self.adb.page.run_task(self.InspectProgress)
            # temp = await asyncio.to_thread(
            #     self.run_parallel, settings, filters, timeout_limit, target_quantity
            # )
            await self.run_parallel_async(
                settings, filters, timeout_limit, target_quantity
            )
        except Exception as ex:
            print(f"seting erro, use default value. {ex}")
        finally:
            await asyncio.sleep(1)
            self.is_computing = False
            # print(f"{temp=}")

    # region InspectProgress
    async def InspectProgress(self):
        await asyncio.sleep(0.5)
        _last_value = -1
        _last_count = 0
        while self.is_computing:
            await asyncio.sleep(1)
            if _last_value == self.taskbar_value:
                continue
            self.showbar.value = f"Task {self.taskbar_value * 100:.0f}% Complete"
            self.taskbar.value = self.taskbar_value
            self.taskbar.update()
            self.showbar.update()
            _last_value = self.taskbar_value
            current_count = len(self.valid_results)
            if current_count > _last_count:
                # 利用切片获取自上次检查以来新增的所有数据
                new_items = self.valid_results[_last_count:current_count]
                # 遍历打印出新发现的数据
                for item in new_items:
                    # print(f"🎉 发现新数据: {item}")
                    if self.additem and self.removeitem:
                        self.additem(self.removeitem, item)

                # 更新计数器
                _last_count = current_count
        await asyncio.sleep(1)
        self.showbar.value = (
            f"Core-Link Parallelizer found {self.valid_results.__len__()} items."
        )
        print(f"Core-Link Parallelizer found {self.valid_results.__len__()} items.")
        self.showbar.update()

    # endregion

    # region __builde_conter
    def __builde_conter(self):
        title = ft.Column(
            tight=True,
            width=float("inf"),
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Core-Link Parallelizer", size=18, color=DraculaColors.FOREGROUND
                ),
                ft.Text(
                    "Scaling heavy computations through seamless Joblib-driven parallelization.",
                    size=14,
                    color=ft.Colors.with_opacity(0.4, DraculaColors.FOREGROUND),
                ),
            ],
        )
        jobsetting = ft.Column(
            tight=True,
            width=float("inf"),
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "timeout limit:",
                            size=15,
                            color=ft.Colors.with_opacity(1, DraculaColors.FOREGROUND),
                        ),
                        in_timeout := ft.TextField(
                            hint_text="60 seconds",
                            border=ft.InputBorder.NONE,
                            cursor_height=15,
                            text_size=15,
                            dense=True,
                            content_padding=ft.Padding.all(0),
                        ),
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            "target quantity:",
                            size=15,
                            color=ft.Colors.with_opacity(1, DraculaColors.FOREGROUND),
                        ),
                        in_target_quantity := ft.TextField(
                            hint_text="0 quantity",
                            border=ft.InputBorder.NONE,
                            cursor_height=15,
                            text_size=15,
                            dense=True,
                            content_padding=ft.Padding.all(0),
                        ),
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Maximum Calculation Time:",
                            size=15,
                            color=ft.Colors.with_opacity(1, DraculaColors.FOREGROUND),
                        ),
                        in_max_time := ft.TextField(
                            hint_text="5 minutes",
                            border=ft.InputBorder.NONE,
                            cursor_height=15,
                            text_size=15,
                            dense=True,
                            content_padding=ft.Padding.all(0),
                        ),
                    ]
                ),
                ft.Row(height=5),
                ft.Row(
                    controls=[
                        showbar := ft.Text(
                            "The task has not yet started.",
                            size=15,
                            italic=True,
                            color=RandColor(mode="neon"),
                        ),
                    ]
                ),
                ft.Row(
                    controls=[
                        tbar := ft.ProgressBar(
                            value=0.5,
                            expand=1,
                            height=10,
                            color=RandColor(mode="neon"),
                            border_radius=5,
                        ),
                    ],
                ),
            ],
        )
        self.intimeout = in_timeout
        self.intargetquantity = in_target_quantity
        self.inmaxtime = in_max_time
        self.taskbar = tbar
        self.showbar = showbar
        acts = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.TextButton(
                    "Cancel",
                    on_click=self.handle_cancel,
                    style=ft.ButtonStyle(
                        color=ft.Colors.with_opacity(0.8, DraculaColors.FOREGROUND)
                    ),
                ),
                # 确定按钮用红色突出显示危险操作
                ft.TextButton(
                    "Start",
                    on_click=self.handle_start,
                    style=ft.ButtonStyle(color=RandColor(hue="blue")),
                ),
            ],
        )
        conter = ft.Container(
            # width=400,
            padding=5,
            border_radius=0,
            content=ft.Column(
                tight=True,
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    title,
                    jobsetting,
                    ft.Divider(color=DraculaColors.FOREGROUND),
                    acts,
                ],
            ),
        )
        return conter

    # endregion

    # region run_parallel_async
    async def run_parallel_async(self, settings, filters, timeout=60, Quantity=0):
        """
        使用 joblib 执行多进程计算

        :param settings: dict, 必填，计算设置
        :param filters: dict, 必填，过滤校验规则
        :param timeout: int, 运行时长(秒)，默认 60 为0 则不限制执行时间
        :param Quantity: int, 需要的正确结果数量，默认 10。如果为 0 则不限制数量。
        :return: list, 满足条件的计算结果列表
        """
        if not settings or not filters:
            return self.valid_results

        self.valid_results = []
        self.taskbar_value = 0
        start_time = time.time()
        loop = asyncio.get_running_loop()

        # print(f'{self.adb.page.platform=}')
        # 1. 环境适配
        is_mobile = self.adb.page.platform in [
            ft.PagePlatform.ANDROID,
            ft.PagePlatform.ANDROID_TV,
        ]
        if is_mobile:
            executor_class = ThreadPoolExecutor
            n_cores = 2
            chunk_size = 50  # 增加单次任务量
            batch_count = 4  # 减少并发批次
        else:
            executor_class = ProcessPoolExecutor
            n_cores = multiprocessing.cpu_count()
            chunk_size = 20
            batch_count = n_cores * 2

        # 使用 executor
        with executor_class(max_workers=n_cores) as executor:
            while True:
                elapsed = time.time() - start_time
                if elapsed >= timeout or self.Launch_Cancelled == "launch":
                    break

                if Quantity > 0 and len(self.valid_results) >= Quantity:
                    break

                # 2. 创建一批任务
                # 注意：我们将任务存入一个集合 (set) 中进行管理
                tasks = {
                    loop.run_in_executor(
                        executor, calculate_batch_wrapper, settings, filters, chunk_size
                    )
                    for _ in range(batch_count)
                }

                # 3. 【核心修复】：使用 asyncio.wait 代替 as_completed
                # 这样我们可以完全控制每一个 Future 的生命周期
                while tasks:
                    if (time.time() - start_time) >= timeout or (
                        Quantity > 0 and len(self.valid_results) >= Quantity
                    ):
                        break

                    # 等待最先完成的一个或多个任务
                    done, pending = await asyncio.wait(
                        tasks,
                        timeout=1.0,  # 给个小超时，防止死锁并方便检查外部打断
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    # 更新 tasks 集合，只保留还在运行的任务
                    tasks = pending

                    for completed_task in done:
                        try:
                            batch_res_list = await completed_task
                            if batch_res_list:
                                for res in batch_res_list:
                                    self.valid_results.append(res)
                                    # print(f'{len(self.valid_results)}')
                                    if (
                                        Quantity > 0
                                        and len(self.valid_results) >= Quantity
                                    ):
                                        # print("ren wu wangcheng tiqian tuichu")
                                        break
                        except Exception as e:
                            print(f"run_parallel_async Calculation error: {e}")
                    if Quantity == 0:
                        self.taskbar_value = (time.time() - start_time) / timeout
                    else:
                        self.taskbar_value = self.valid_results.__len__() / Quantity

                # 4. 【关键清理】：如果本批次循环结束仍有正在跑的任务，强制取消
                if tasks:
                    for t in tasks:
                        t.cancel()
                    # 显式吞掉取消可能引发的异常，确保不报警告
                    await asyncio.gather(*tasks, return_exceptions=True)
            executor.shutdown(wait=True, cancel_futures=True)
        # print("fanhui shuju")
        self.taskbar_value = 1
        self.Launch_Cancelled = "none"
        return self.valid_results[:Quantity] if Quantity > 0 else self.valid_results

    # endregion


# endregion


# region operates
class operates:
    def __init__(self):
        self.conten = self.__builde_conter()
        self.adb = adbx(None, self.conten)
        self.callback = None

    def setting_callback(self, callback=None):
        self.callback = callback

    def handle_cancel(self):
        self.adb.page.pop_dialog()

    def handle_cilck(self, e, data: str = "none"):
        if self.callback:
            kwargs = {"max_count": 1000, "data": data}
            self.adb.page.run_task(self.callback, **kwargs)

    def __builde_conter(self):
        def hover(e, item):
            if not e.data:
                item.size = 17
            else:
                item.size = 15

        title = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    "Operates", size=18, weight="bold", color=DraculaColors.FOREGROUND
                ),
                ft.IconButton(
                    icon=ft.Icon(ft.Icons.CANCEL, color=DraculaColors.FOREGROUND),
                    icon_size=20,
                    tooltip=ft.Tooltip(message="Cancel Clear"),
                    on_click=self.handle_cancel,
                ),
            ],
        )
        clear_all = ft.Container(
            padding=5,
            content=ft.Row(
                controls=[
                    flg := ft.Icon(ft.Icons.CLEAR_ALL, size=15),
                    ft.Text(
                        "Clear All Results",
                        size=15,
                        color=RandColor(hue="red"),
                    ),
                ]
            ),
            on_hover=lambda e, x=flg: hover(e, x),
            on_click=lambda e, data="all": self.handle_cilck(e, data),
        )
        clear_select = ft.Container(
            padding=5,
            content=ft.Row(
                controls=[
                    flg := ft.Icon(ft.Icons.SELECT_ALL, size=15),
                    ft.Text(
                        "Clear All Selected items",
                        size=15,
                        color=RandColor(hue="green"),
                    ),
                ]
            ),
            on_hover=lambda e, x=flg: hover(e, x),
            on_click=lambda e, data="select": self.handle_cilck(e, data),
        )
        clear_unselected = ft.Container(
            padding=5,
            content=ft.Row(
                controls=[
                    flg := ft.Icon(ft.Icons.UNPUBLISHED, size=15),
                    ft.Text(
                        "Clear all unselected items",
                        size=15,
                        color=RandColor(hue="blue"),
                    ),
                ]
            ),
            on_hover=lambda e, x=flg: hover(e, x),
            on_click=lambda e, data="unselected": self.handle_cilck(e, data),
        )

        conter = ft.Container(
            padding=5,
            border_radius=0,
            content=ft.Column(
                tight=True,
                spacing=5,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    title,
                    ft.Divider(height=1, color=DraculaColors.FOREGROUND),
                    clear_all,
                    clear_select,
                    clear_unselected,
                ],
            ),
        )
        return conter


# endregion


# region itemslist_long_pess
class promptdlg:
    def __init__(
        self,
        title: str = "info",
        info: str = "this is test abd dlg.",
        typecolor: str = "info",
        exittime: int = 7,
    ):
        self.nowait = False
        self.exittime = exittime
        self.typecolor = self.gettypecolor(typecolor)
        self.conten = self.__builde_conter(title, info)
        self.adb = adbx(None, self.conten)
        self.adb.setting_did_mount_callback(self.AutoPopDlg)

    def settinginfo(self, **kwargs):
        raise AttributeError("settinginfo Deleted. Usage is prohibited.")

    def gettypecolor(self, typecolor: str):
        color = "#ffffff"
        match typecolor.lower():
            case "info":
                color = RandColor(mode="neon", hue="blue")
            case "warning":
                color = RandColor(mode="neon", hue="yellow")
            case "error":
                color = RandColor(mode="neon", hue="red")
        return color

    def handle_close(self):
        self.adb.page.pop_dialog()

    def handle_click_nowait(self):
        self.nowait = True

    async def AutoPopDlg(self):
        count = self.exittime
        while count != 0:
            if self.nowait:
                break
            self.exitinfo.value = f"Disappears in {count} seconds."
            if self.adb.page:
                self.exitinfo.update()
            await asyncio.sleep(1)
            count -= 1

        self.handle_close()

    def __builde_conter(self, title: str, info: str):
        title = ft.Text(
            f"{title}",
            size=16,
            weight="bold",
            color=self.typecolor,
        )
        info = ft.Text(
            f"{info}",
            size=14,
            color=self.typecolor,
        )
        exitinfo = ft.Text(
            f"Disappears in {self.exittime} seconds.",
            size=12,
            color=ft.Colors.with_opacity(0.7, DraculaColors.FOREGROUND),
        )

        onter = ft.Container(
            padding=5,
            border_radius=0,
            content=ft.Column(
                tight=True,
                spacing=5,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[title, info, exitinfo],
            ),
            on_click=self.handle_click_nowait,
        )
        self.exitinfo = exitinfo
        return onter


# endregion


# region Lotterpng
class Lotterpng:
    def __init__(self):
        self.content = self.__build_content()
        self.adb = adbx(None, self.content)
        self.adb.setting_did_mount_callback(self.AutoPopDlg)
        self.render_image = None
        self.genid = ""

    def seting_get_all_exp(self, getallexp=None):
        self.getallexp = getallexp

    def setting_cancel(self, cancel_callback=None):
        self.cancel_callback = cancel_callback

    def __build_content(self):
        title = ft.Row(
            tight=True,
            controls=[
                ft.Icon(
                    icon=ft.Icons.IMAGE,
                    size=16,
                    color=DraculaColors.FOREGROUND,
                ),
                infotext := ft.Text(
                    value="Lottery Rendering",
                    size=16,
                    color=DraculaColors.FOREGROUND,
                ),
            ],
        )
        progress = ft.ProgressBar(value=0, bar_height=1, color=RandColor(mode="neon"))
        content = ft.Container(
            padding=5,
            border_radius=0,
            content=ft.Column(
                tight=True,
                spacing=5,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[title, progress],
            ),
        )
        self.progress = progress
        self.infotext = infotext
        return content

    def handle_close(self):
        self.adb.page.pop_dialog()

    def handle_click_nowait(self):
        self.nowait = True

    def load_exp(self) -> list | None:
        if self.getallexp:
            allexp = self.getallexp()
            return allexp

    async def AutoPopDlg(self):
        exp = self.getallexp(max_count=100)
        total = len(exp)
        if total == 0:
            self.handle_close()
            return

        def sync_callback(val, desc):
            # 内部函数，用于在 Flet 中更新
            self.progress.value = val
            self.infotext.value = desc
            self.infotext.update()
            self.progress.update()

        # 将同步回调封装为线程安全的调用
        def thread_safe_callback(val, desc):
            # 使用 page.run_threadsafe 或者简单的 loop.call_soon_threadsafe
            # 在 Flet 中，直接修改值并 update 也是可以的，但更严谨的做法是：
            self.adb.page.loop.call_soon_threadsafe(sync_callback, val, desc)

        # 在后台执行整个渲染任务
        await asyncio.to_thread(self.render_lotter_sync, thread_safe_callback, exp)
        await asyncio.sleep(0.5)
        print(f"render_image sizeof {self.render_image.__sizeof__()}")
        is_mobile_or_web = self.adb.page.web or self.adb.page.platform in [
            ft.PagePlatform.ANDROID,
            ft.PagePlatform.IOS,
        ]
        try:
            png_name = f"{self.genid}.png"
            save_png = await ft.FilePicker().save_file(
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["png"],
                file_name=png_name,
                src_bytes=self.render_image,
            )
            # print(f"save_path: {save_png}")
            if save_png and not is_mobile_or_web:
                with open(save_png, "wb") as f:
                    f.write(self.render_image)
        except Exception as er:
            print(f"Image saving error. {er}")
        finally:
            await asyncio.sleep(1)
            self.handle_close()

    def style_config(self):
        return {
            "background": {"fill": "#172433", "opacity": 1, "buffer": True},
            "image": {
                "filepath": f"{env_manager.app_assets_dir}/1fa7acf2.png",
                "rotate": -17.89,
                "opacity": 0.5,
                "top": 0,
                "buffer": True,
            },
            "title": {
                "text": "Today’s Super Jackpot",
                "name": "RacingSansOne-Regular",
                "textsize": 60,
                "text_color": "#FFD000",
            },
            "line": {
                # "text": "01 05 08 10 11 16 17 18 20 56 78 90",  # 文字内容
                "name": "Inter_18pt-SemiBold",  # 字体
                "textsize": 30,  # 字号
                "text_color": "#ffffff",  # 文字颜色
                "padding_x": 10,  # 左右撑开 40px
                "padding_y": 10,  # 上下撑开 20px
                "stroke_width": 0,
                "bg_fill": "#6b29ce",  # 背景颜色（绿色）
                "bg_rx": 5,  # 大圆角
                "bg_stroke": "#ffffff",  # 白色边框
                "bg_stroke_width": 1,
                "bg_opacity": 0.45,
                "margin_bottom": 10,  # 下方留白
                "expand": True,
            },
            "spacing": {"height": 10},
            "text": {
                # "text": "Activity rules:\n1. Participate in the lottery\n2. Get rewards\n3. 祝您中的大奖\n4. 宝くじが当たりますように！",
                "name": "NotoSansSC-Regular",
                "textsize": 24,
                "align": "left",
                "stroke_width": 0,
                "text_color": RandColor(mode="neon"),
                "opacity": 1,
            },
            "circle": {
                "size": 45,
                "fill": "#FF0000",
                "text_color": "#FFFF00",
                "opacity": 0.9,
            },
        }

    def render_lotter_sync(self, progress_callback, exp_line: list = None):
        """
        关键词说明
        - self
        - exp_line ["09 10 11 18 19 20 + 14"..]
        """
        if exp_line:
            exp_lines = exp_line
        else:
            # 没有设置getallexp直接退出
            return
        style_conf = self.style_config()
        renderer = Rendering(width=400 * 2, height=888 * 2, padding=30, level=0)

        total = len(exp_lines)
        print(f"exp len {total} Start progress report.")
        (
            renderer.set_background(**style_conf["background"])
            .add_title(**style_conf["title"])
            .add_image(**style_conf["image"])
        )
        progress_callback(0.1, "Background theme rendering completed")
        # 返回进度和描述
        # 渲染 文件头
        for index, line_text in enumerate(exp_lines, start=1):
            # 构建参数
            exp_conf = {
                "text": f"{index}: {line_text}",
                "text_color": RandColor(mode="neon"),
                "bg_fill": RandColor(mode="neon"),
            }
            line_conf = style_conf["line"]
            line_conf.update(exp_conf)
            renderer.add_text_with_bg(**line_conf)
            if index % 5 == 0 and index != len(exp_lines):
                renderer.add_spacing(**style_conf["spacing"])
                text_conf = style_conf["text"]
                info_conf = {
                    "text": "God of Wealth Divider.",
                    "text_color": RandColor(mode="neon"),
                }
                text_conf.update(info_conf)
                renderer.add_text(**text_conf)
            # 计算进度：从 0.1 到 0.9 之间分配给数据行
            progress = 0.1 + ((index - 1) / total) * 0.8
            progress_callback(progress, f"Processing line {index}/{total}")

        renderer.add_text(
            text="☀ 动动手指, 把藏在云端的幸运领回家.\n☀ 财神爷正在敲门, 请准备好大大的口袋.\n☀ 选下你的心仪数字, 开启一份对生活的期待.",
            name="NotoSansSC-Regular",
            textsize=24,
            align="left",
            text_color=RandColor(mode="neon"),
        )
        # now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.genid = randomData.generate_secure_string(8)
        renderer.add_text(
            text=f"⊕ {now} {self.genid}",
            name="NotoSansSC-Regular",
            textsize=24,
            align="right",
            text_color=RandColor(mode="neon"),
        )
        # renderer.save(filepath="./sde.png")
        self.render_image = renderer.RetrieveBytes()
        progress_callback(1.0, "Rendering completed.")


# endregion
