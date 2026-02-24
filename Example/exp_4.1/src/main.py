# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-02-03 04:18:31
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-03 05:47:40
import traceback
from turtle import bgcolor
import flet as ft
import random
import os
import string
import asyncio

app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
os.environ["FLET_SECRET_KEY"] = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

content = """
    The bug in the Android version of Filepicker has been reproduced.
This will demonstrate how to save a file.
And successfully reproduce the bug. 

    filepicker 安卓版 bug 复现.
这里将演示如何保存一个文件.
并成功复刻出bug.

    Android版Filepickerのバグ再現。ファイルの保存方法を説明します。
バグは再現されました。

    The text above will be saved to a file, 
with the goal of making it work on all platforms.
"""


def main(page: ft.Page):
    file_picker = ft.FilePicker()
    content_bytes = content.encode("utf-8")
    is_mobile_or_web = page.web or page.platform in [
        ft.PagePlatform.ANDROID,
        ft.PagePlatform.IOS,
    ]
    
    async def handle_on_upload(e):
        await asyncio.sleep(0.5)
        if e.progress == 1.0 and e.error == None:
            filepath = os.path.join(app_temp_path, e.file_name)
            with open(filepath, "r", encoding="utf-8") as f:
                markdown.value = f.read()
                markdown.update()
            os.remove(filepath)


    async def handle_pick_files(e: ft.Event[ft.Button]):
        try:
            files = await file_picker.pick_files(allow_multiple=True)
            selected_files.value = (
                ", ".join(map(lambda f: f.name, files)) if files else "Cancelled!"
            )
            if files and is_mobile_or_web:
                file_picker.on_upload = handle_on_upload
                upfiles = [
                    ft.FilePickerUploadFile(
                        page.get_upload_url(files[0].name, 600),
                        "PUT",
                        None,
                        files[0].name,
                    )
                ]
                await file_picker.upload(upfiles)
        except Exception:
            traceback.print_exc()

    async def handle_save_file(e: ft.Event[ft.Button]):
        try:
            save_path = await file_picker.save_file(
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["text"],
                file_name="content_bytes.text",
                src_bytes=content_bytes,
            )
            if save_path and not is_mobile_or_web:
                with open(save_path, "wb") as f:
                    f.write(content_bytes)
                print("Desktop file save complete. [ linux windows and macos ]")
        except Exception:
            traceback.print_exc()

    page.add(
        ft.Column(
            expand=True,
            controls=[
                ft.Button(
                    content="Pick files",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=handle_pick_files,
                ),
                selected_files := ft.Text(),
                ft.Divider(),
                markdown :=ft.Markdown(
                    value='**Waiting for upload** `flutter 3.38.9`, `flet 0.80.5`',
                    height=300,
                    width=900,
                ),
                ft.Divider(),
                ft.Button(
                    content="Save file",
                    icon=ft.Icons.SAVE,
                    on_click=handle_save_file,
                ),
            ],
        ),
    )


ft.run(main,  upload_dir=app_temp_path)
