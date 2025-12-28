# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-26 05:56:59
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2025-12-26 06:06:59
import flet as ft


def main(page: ft.Page):
    counter = ft.Text("100", size=50, data=0)

    def increment_click(e):
        counter.data += 1
        counter.value = str(counter.data)
        counter.update()

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=increment_click
    )
    page.add(
        ft.SafeArea(
            ft.Container(
                counter,
                alignment=ft.alignment.center,
            ),
            expand=True,
        )
    )


ft.app(main)
