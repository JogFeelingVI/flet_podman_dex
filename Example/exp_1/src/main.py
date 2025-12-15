# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-13 05:50:51
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2025-12-13 06:21:40
import click
import flet as ft


def main(page: ft.Page):
    page.title = 'Example 1 flet code'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    text_number = ft.TextField(value=0, width=100,text_align=ft.TextAlign.RIGHT)

    def jian_click(e):
        text_number.value = str(int(text_number.value) - 1)
        page.update()
        
    def jia_click(e):
        text_number.value = str(int(text_number.value) + 1)
        page.update()
    
    

    
    page.add(
        ft.SafeArea(
            ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.REMOVE, on_click=jian_click),
                    text_number,
                    ft.IconButton(icon=ft.Icons.ADD, on_click=jia_click),
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER
            ),
            expand=True,
        )
    )


ft.app(main)
