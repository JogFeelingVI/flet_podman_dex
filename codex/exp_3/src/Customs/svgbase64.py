# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-13 07:14:33
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-23 01:46:06

import base64


def svgimage(number, stroke_color="#FFFFFF"):
    # SVG 模板：关键在于 text 标签的定位属性
    if isinstance(number, str):
        number = int(number)
    svg_code = f"""
    <svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <!-- 正圆边框:cx/cy 是圆心 r 是半径 -->
        <circle cx="100" cy="100" r="90" fill="none" stroke="{stroke_color}" stroke-width="8" />
        
        <!-- 居中数字 -->
        <text x="42" y="136"
              font-family="JetBrainsMono-Bold" 
              font-size="100" 
              font-weight="bold"
              fill="{stroke_color}">
            {number:02d}
        </text>
    </svg>
    """
    # 转换为 Base64 给 Flet 使用
    b64_str = base64.b64encode(svg_code.encode("utf-8")).decode("utf-8")
    return b64_str


def check_select(bgcolor: str = "#7f7f7f", color: str = "#0ce829"):
    """黑色圆圈背景 绿色的对号"""
    svg_code = f"""
    <svg width="500" height="500" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
    <!-- Created with SVG-edit - https://github.com/SVG-Edit/svgedit-->
    <g class="layer">
    <title>Layer 1</title>
    <ellipse cx="207.053951" cy="255.941901" fill="{bgcolor}" id="svg_1" opacity="0.35" rx="200.053951" ry="200.053951" stroke="#000000" stroke-width="0"/>
    <path d="m67.622409,274.128624c-2.020747,-2.020747 101.037349,119.224072 101.037349,119.224072c0,0 325.340263,-264.717854 325.340263,-264.717854c0,0 -78.809132,-70.726144 -78.809132,-70.726144c0,0 -232.385902,270.780095 -232.385902,270.780095c0,0 -74.767638,-103.058096 -74.767638,-103.058096c0,0 -40.41494,48.497927 -40.41494,48.497927z" fill="{color}" id="svg_3" stroke="#7c6767"/>
    </g>
    </svg>
    """
    b64_str = base64.b64encode(svg_code.encode("utf-8")).decode("utf-8")
    return b64_str


def itemText():
    svg_code = """
    <svg width="299" height="33" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
    <!-- Created with SVG-edit - https://github.com/SVG-Edit/svgedit-->
    <g class="layer">
    <title>Layer 1</title>
    <text fill="#000000" font-family="Serif" font-size="24" id="svg_2" stroke="#000000" stroke-width="0" text-anchor="middle" transform="matrix(1.17426 0 0 1.17426 141.382 -8.66728)" x="22.34" xml:space="preserve" y="30.65">02 03 04 05 06 07 + 19</text>
    <g id="svg_6" transform="translate(-4.88 -6.28) matrix(0.565259 -0.32813 0.32813 0.565259 -150.525 83.4378)">
    <ellipse cx="273.83" cy="52" fill="none" id="svg_3" rx="18" ry="18" stroke="#000000" stroke-width="3"/>
    <text fill="#000000" font-family="Serif" font-size="24" id="svg_5" stroke="#000000" stroke-width="0" text-anchor="middle" transform="matrix(1.46667 0 0 1.46667 -48.9949 -174)" x="219.91" xml:space="preserve" y="161.93">A</text>
    </g>
    </g>
    </svg>
    """
