# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 04:20:46
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-04 00:29:45

from flet import (
    ButtonTheme,
    IconTheme,
    NavigationBarTheme,
    SnackBarTheme,
    TextButtonTheme,
    Theme,
)
from flet import TextStyle, FontWeight, TextTheme


class Dracula_colors:
    """定义德古拉配色方案"""

    BACKGROUND = "#282a36"
    CURRENT_LINE = "#44475a"
    FOREGROUND = "#f8f8f2"
    COMMENT = "#6272a4"
    PURPLE = "#bd93f9"
    PINK = "#ff79c6"
    CYAN = "#8be9fd"
    GREEN = "#50fa7b"
    ORANGE = "#ffb86c"
    RED = "#ff5555"
    YELLOW = "#f1fa8c"


# Dracula_Theme = Theme(
#     color_scheme={
#         "primary": Dracula_colors.PURPLE,
#         "on_primary": Dracula_colors.FOREGROUND,
#         "primary_container": Dracula_colors.CURRENT_LINE,
#         "on_primary_container": Dracula_colors.FOREGROUND,
#         "secondary": Dracula_colors.PINK,
#         "on_secondary": Dracula_colors.FOREGROUND,
#         "secondary_container": Dracula_colors.CURRENT_LINE,
#         "on_secondary_container": Dracula_colors.FOREGROUND,
#         "tertiary": Dracula_colors.CYAN,
#         "on_tertiary": Dracula_colors.FOREGROUND,
#         "tertiary_container": Dracula_colors.CURRENT_LINE,
#         "on_tertiary_container": Dracula_colors.FOREGROUND,
#         "error": Dracula_colors.RED,
#         "on_error": Dracula_colors.FOREGROUND,
#         "error_container": Dracula_colors.RED,
#         "on_error_container": Dracula_colors.FOREGROUND,
#         "background": Dracula_colors.BACKGROUND,
#         "on_background": Dracula_colors.FOREGROUND,
#         "surface": Dracula_colors.CURRENT_LINE,
#         "on_surface": Dracula_colors.FOREGROUND,
#         "surface_variant": Dracula_colors.COMMENT,
#         "on_surface_variant": Dracula_colors.FOREGROUND,
#         "outline": Dracula_colors.COMMENT,
#     },
#     button_theme=ButtonTheme(
#         style=TextStyle(color=Dracula_colors.COMMENT, weight=FontWeight.BOLD)
#     ),
#     text_button_theme=TextButtonTheme(
#         style=TextStyle(color=Dracula_colors.COMMENT, weight=FontWeight.BOLD)
#     ),
#     snackbar_theme=SnackBarTheme(
#         bgcolor=Dracula_colors.CURRENT_LINE,
#         content_text_style=TextStyle(color=Dracula_colors.FOREGROUND),
#     ),
#     navigation_bar_theme=NavigationBarTheme(
#         bgcolor=Dracula_colors.BACKGROUND,
#         indicator_color=Dracula_colors.CURRENT_LINE,
#         label_text_style=TextStyle(
#             color=Dracula_colors.COMMENT, weight=FontWeight.BOLD
#         ),
#     ),
#     icon_theme=IconTheme(
#         color=Dracula_colors.COMMENT,
#     ),
#     text_theme=TextTheme(
#         title_large=TextStyle(color=Dracula_colors.COMMENT, weight=FontWeight.BOLD),
#         title_medium=TextStyle(color=Dracula_colors.COMMENT, weight=FontWeight.BOLD),
#         title_small=TextStyle(color=Dracula_colors.COMMENT, weight=FontWeight.BOLD),
#         body_large=TextStyle(color=Dracula_colors.FOREGROUND),
#         body_medium=TextStyle(color=Dracula_colors.FOREGROUND),
#         body_small=TextStyle(color=Dracula_colors.FOREGROUND),
#         headline_large=TextStyle(color=Dracula_colors.PINK, weight=FontWeight.BOLD),
#         headline_medium=TextStyle(color=Dracula_colors.PINK, weight=FontWeight.BOLD),
#         headline_small=TextStyle(color=Dracula_colors.PINK, weight=FontWeight.BOLD),
#     ),
# )
