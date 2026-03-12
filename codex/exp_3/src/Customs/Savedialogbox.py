# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-02 09:10:57
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-12 09:03:55


from .jackpot_core import randomData, filter_for_pabc
from .DraculaTheme import DraculaColors, RandColor, HarmonyColors
from .adbox import adbx
from .asyncredis import RedisAPI
from dataclasses import dataclass, field
import asyncio
import flet as ft
import datetime
import json


# region _savedialog
class savedialog:
    def __init__(self):
        self.conten = self.__builde_conter()
        self.adb = adbx(None, self.conten)
        self.adb.setting_did_mount_callback(self.load_exp)
        self.exps_is_build = True
        self.getallexp = None

    def seting_get_all_exp(self, getallexp=None):
        self.getallexp = getallexp

    def __builde_conter(self):
        title_color = DraculaColors.ORANGE
        text_color = HarmonyColors(
            base_hex_color=title_color, harmony_type="analogous", mode="neon"
        )
        act_color = HarmonyColors(
            base_hex_color=title_color, harmony_type="split", mode="neon"
        )
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.genid = randomData.generate_secure_string(8)
        footer = ft.Row(
            controls=[ft.Text(f"{now} {self.genid}", size=14, color=text_color[0])],
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
            spacing=5,
        )
        acts = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.TextButton(
                    "Cancel",
                    on_click=self.__handle_cancel,
                    style=ft.ButtonStyle(color=act_color[0]),
                ),
                # 确定按钮用红色突出显示危险操作
                ft.TextButton(
                    "Save to png",
                    on_click=self.__handle_save,
                    style=ft.ButtonStyle(color=act_color[1]),
                ),
            ],
        )

        conter = ft.Container(
            # width=400,
            padding=5,
            border_radius=6,
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
        self.Screenshot = ft.Screenshot(content=conter)
        content = ft.Column(
            controls=[self.Screenshot],
            tight=True,
        )
        return content

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

    def __handle_cancel(self):
        if self.adb.running:
            self.adb.page.pop_dialog()

    def CreateItem(self, text: str = "", i=0):
        userColor = RandColor(mode="neon")
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

    async def __handle_save(self):
        if self.exps_is_build:
            is_mobile_or_web = self.adb.page.web or self.adb.page.platform in [
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
                        self.adb.page.show_dialog(
                            ft.SnackBar(f"{self.adb.page.platform} file save complete.")
                        )
                # print(f"Storage task completed.")
            except Exception as er:
                # print(f"Image saving error.")
                pass
            finally:
                await asyncio.sleep(1)
                self.adb.page.pop_dialog()


# endregion


# region _tadbx
@dataclass
class TaskState:
    result: list = field(default_factory=list)
    info: str = ""
    task: str = "none"

    async def addinfo(self, text: str) -> str:
        self.info = f"{text}"
        await asyncio.sleep(0.3)

    def getinfo(self) -> str:
        info = self.info
        self.info = None
        return info

    def additem(self, item):
        self.result.append(item)

    def getitems(self, sord: bool = False):
        if sord == False:
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
            self.adb.page.run_task(self.Detection)
            self.adb.page.run_task(self.showresult)

    async def Detection(self):
        await self.detectstatus.addinfo("Load 'settings' and 'filters' data.")
        # await asyncio.sleep(0.3)
        settings = self.adb.page.session.store.get("settings")
        filtersAll = self.adb.page.session.store.get("filters")
        if not filtersAll:
            await self.detectstatus.addinfo("If filters is empty, skip the detection.")
            # await asyncio.sleep(0.3)
            self.detectstatus.task = "none"
            return

        await self.detectstatus.addinfo("Create a data pool.")
        if settings and filtersAll:
            _rdpn = randomData(seting=settings["randomData"])
            results = []
            for i in range(1000):
                results.append(_rdpn.get_pabc())
        await asyncio.sleep(0.3)
        for _fitem in filtersAll:
            # print(f"{_fitem}")
            _f2func = filter_for_pabc(filters=[_fitem])
            pass_rate = (
                sum([1 for r in results if _f2func.handle(r)]) / len(results) * 100
            )
            prinfo = [
                f"{_fitem['func']}",
                f"{_fitem['target']}",
                f"{_fitem['condition']}",
                int(pass_rate),
            ]
            self.detectstatus.additem(prinfo)
            await self.detectstatus.addinfo(f"{_fitem['condition']} Test completed.")
        # await asyncio.sleep(0.3)
        await self.detectstatus.addinfo("Data sorting.")
        sorted_data = sorted(self.detectstatus.getitems(True), key=lambda x: x[-1])
        max_num = max(item[-1] for item in sorted_data)
        min_num = min(item[-1] for item in sorted_data)
        self.detectstatus.result = sorted_data[0:9]
        zuida = f"Max {max_num} Min: {min_num} filters len {len(filtersAll)}"
        await self.detectstatus.addinfo(zuida)
        # await asyncio.sleep(0.3)
        self.detectstatus.task = "sorted"

    async def showresult(self):
        while self.detectstatus.task == "Detection":
            await asyncio.sleep(0.3)
            text = self.detectstatus.getinfo()
            if text:
                if self.info_display.controls.__len__() >= 10:
                    self.info_display.controls.pop(0)
                self.info_display.controls.append(self.info(text))
                self.info_display.update()
        while self.detectstatus.task == "sorted":
            await asyncio.sleep(0.3)
            if self.info_display.controls.__len__() >= 10:
                self.info_display.controls.pop(0)
            popItem = self.detectstatus.result.pop(0)
            self.info_display.controls.append(self.info(*popItem))
            self.info_display.update()
            if self.detectstatus.result.__len__() == 0:
                self.detectstatus.task = "none"
        self.info_display.controls.append(self.info("Test complete ✔"))
        self.info_display.update()

    def __builde_conter(self):
        title_color = DraculaColors.ORANGE
        text_color = HarmonyColors(
            base_hex_color=title_color, harmony_type="analogous", mode="neon"
        )
        act_color = HarmonyColors(
            base_hex_color=title_color, harmony_type="split", mode="neon"
        )
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
            spacing=3,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    expand=1,
                    height=65,
                    # 1. 删除 padding=10，避免上下空间被挤压
                    # 2. 加上 alignment，让内部文字完美水平+垂直居中
                    alignment=ft.Alignment.CENTER,
                    border_radius=10,
                    bgcolor=ft.Colors.TRANSPARENT,
                    border=ft.Border.all(
                        1, ft.Colors.with_opacity(0.5, DraculaColors.FOREGROUND)
                    ),
                    content=ft.Text(
                        "78",
                        size=40,
                        color="#80fa42",
                        # text_align="center" # 其实加了 alignment 后，这个可以不写了
                    ),
                ),
                ft.Container(
                    expand=1,
                    height=65,
                    alignment=ft.Alignment.CENTER,  # 同上，完美居中
                    border_radius=10,
                    bgcolor=ft.Colors.TRANSPARENT,
                    border=ft.Border.all(
                        1, ft.Colors.with_opacity(0.5, DraculaColors.FOREGROUND)
                    ),
                    content=ft.Text("23", size=40, color="#fc3131"),
                ),
            ],
        )
        self.info_display = ft.Column(
            tight=True,
            spacing=3,
            scroll=ft.ScrollMode.HIDDEN,
            controls=[
                ft.Text(
                    "Click the `Start testing` to begin the test.", color=text_color[0]
                ),
            ],
        )
        acts = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.TextButton(
                    "Close",
                    on_click=self.__handle_Close,
                    style=ft.ButtonStyle(color=act_color[0]),
                ),
                # 确定按钮用红色突出显示危险操作
                ft.TextButton(
                    "Start testing",
                    on_click=self.__handle_start,
                    style=ft.ButtonStyle(color=act_color[1]),
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
                controls=[title, maxmin, self.info_display, acts],
            ),
        )
        return conter

    def info(self, *msg):
        bold = False
        size = 14
        spans = []
        for i, m in enumerate(msg):
            if i == len(msg) - 1:
                bold = True
            if isinstance(m, int):
                bold = True
                m = f"{m}%" if m != "0" else f"{m}% ✖"
            spans.append(
                ft.TextSpan(
                    f"{m} ",
                    style=ft.TextStyle(
                        size=size + 1 if bold else size - 1,
                        color=RandColor(mode="neon")
                        if bold
                        else ft.Colors.with_opacity(0.5, RandColor(mode="neon")),
                        weight="bold" if bold else None,
                        italic=bold,
                    ),
                )
            )
            bold = False
        conter = ft.Container(
            padding=0,
            content=ft.Row(
                spacing=5,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # ft.Icon(ft.Icons.INFO, size=size),
                    ft.Text(spans=spans),
                ],
            ),
        )
        return conter


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

    def setting_valid_info(self, jsondata):
        while isinstance(jsondata, str):
            jsondata = json.loads(jsondata)
        self.intoken.value = jsondata["token"]
        self.intoken_url.value = jsondata["url"]
        self.syncsw.value = jsondata["sync"]
        self.valid_data = jsondata
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
        if (
            self.valid_data
            and self.valid_data.get("valid")
            and self.valid_data.get("token") == token
            and self.valid_data.get("url") == token_url
        ):
            self.valid_data["sync"] = self.syncsw.value
            if self.applycallback:
                self.adb.page.run_task(self.applycallback, self.valid_data)
            self.adb.page.pop_dialog()
            return

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
                        "token": token,
                        "url": token_url,
                        "valid": True,
                        "sync": self.syncsw.value,
                    }
                    self.adb.page.run_task(self.applycallback, backdata)

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
        if value == None or value == -1:
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
