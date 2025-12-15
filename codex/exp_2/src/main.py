# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-15 00:52:00
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2025-12-15 06:18:32
import flet as ft
import math


def main(page: ft.Page):
    page.title = "youtebe flet exp 2"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    side_length_a = ft.TextField(
        label="side length A/mm",
        hint_text="Enter side length mm",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    side_length_b = ft.TextField(
        label="side length B/mm",
        hint_text="Enter side length mm",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    side_length_c = ft.TextField(
        label="side length C/mm",
        hint_text="Enter side length mm",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    
    def clear_click(e):
        side_length_a.value = side_length_b.value = side_length_c.value = ''
        page.open(ft.SnackBar(ft.Text(f"ALL Side number is clear.")))
        page.update()
        
    def done_click(e):
        abc = []
        try:
            abc.append(int(side_length_a.value))
            abc.append(int(side_length_b.value))
            abc.append(int(side_length_c.value))
        except:
            page.open(ft.SnackBar(ft.Text(f"Error: Side number is None.")))
            return
        abc.sort()
        a,b,c = abc
        if a+b<=c:
            page.open(ft.SnackBar(ft.Text(f"Error: The input data cannot form a triangle.")))
            return
        s=(a+b+c)/2
        area = math.sqrt(s * (s - a) * (s - b) * (s - c))
        page.open(ft.SnackBar(ft.Text(f"Area: Ttriangle a {a} b {b} {c} area is {area}.")))
            
    page.add(
        ft.Column(
            [
                ft.Text(
                    value="计算物体面积",
                    text_align=ft.TextAlign.RIGHT,
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PURPLE_100,
                ),
                ft.Divider(height=20),
                side_length_a,
                side_length_b,
                side_length_c,
                ft.Divider(height=5),
                ft.Row(
                    [
                        ft.ElevatedButton(text="Clear", color=ft.Colors.RED_100, on_click=clear_click),
                        ft.ElevatedButton(text="Done", color=ft.Colors.GREEN_100, on_click=done_click),
                    ]
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("海伦公式 (Heron's Formula)", weight=ft.FontWeight.BOLD),
                            ft.Text("公式: \(S=\sqrt{p(p-a)(p-b)(p-c)}\)。"),
                            ft.Text("条件: 已知三角形三条边长 \(a,b,c\)。"),
                            ft.Text("步骤:", weight=ft.FontWeight.BOLD),
                            ft.Text("计算半周长 \(p={a+b+c}{2}\)。"),
                            ft.Text("代入公式计算面积 \(S\)。"),
                        ]
                    )
                )
            ]
        )
    )


ft.app(main)
