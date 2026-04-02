# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-13 07:14:33
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-30 03:17:11

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


def upstashicon(A: str = "#4af212", B: str = "#7cff50"):
    svg_code = f"""
    <svg viewBox="0 0 65.420884 82.278618" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg" version="1.1">

    <g class="layer">
    <title>Layer 1</title>
    <g id="layer1" transform="translate(-62.936606,-33.310688)">
    <path d="m124.58,39.38l-7.94,9.81c2.75,2.76 7.87,3.94 10.58,0.7c2.48,-3.51 0.59,-8.19 -2.64,-10.51zm-12.77,15.79l-8.19,10.12c4.58,-0.9 9.28,2.87 10.86,7.08c4.42,10.08 -0.33,22.69 -9.73,28.11c-7.83,5.17 -18.24,5.08 -26.56,1.15c-1.01,-0.28 -1.99,-0.73 -2.97,-1.22l-7.84,9.68c2.38,1.31 5.14,2 7.64,3.01c12.34,4.1 26.76,3.42 37.65,-4.16c12.29,-8.33 18.74,-25.41 12.72,-39.39c-2.39,-6.2 -7.44,-11.69 -13.58,-14.38zm-11.36,14.04l-9.01,11.14c0,0 0,0 0,0c0.01,0.3 0,0.62 -0.04,0.94c-0.35,1.85 -1.59,2.73 -3.1,2.94l-7.98,9.87c0.92,0.39 1.87,0.72 2.85,1c8.9,2.81 19.67,-2.51 22.18,-11.64c0.96,-3.09 0.53,-6.54 -1.97,-8.78c-1.3,-1.33 -2.73,-3.49 -2.93,-5.47z" display="inline" enable-background="accumulate" fill="{A}" fill-rule="evenodd" id="path2"/>
    <path d="m102.76,33.35c-17.74,-0.9 -35.7,12.41 -38.46,30.26c-2.03,12.11 4.64,25.64 16.02,30.49l0,0l7.98,-9.87c-1.96,0.29 -4.36,-0.53 -5.81,-1.72c-7.48,-5.2 -8.67,-16.04 -4.78,-23.81c4.57,-9.87 16.21,-14.58 26.61,-13.76c4,0.29 7.94,1.38 11.48,3.26c0.25,0.35 0.53,0.68 0.84,0.99l7.94,-9.81c-0.24,-0.17 -0.49,-0.33 -0.75,-0.48c-3.86,-2.47 -8.57,-2.95 -12.86,-4.36c-1.53,-0.38 -3.09,-0.68 -4.67,-0.81c-1.17,-0.19 -2.35,-0.32 -3.54,-0.38zm0.91,20.07c-0.94,0 -1.89,0.07 -2.84,0.22c-7.45,1.14 -15.13,7.31 -14.77,15.39c0.29,4.33 5.2,7.02 5.38,11.32l9.01,-11.14c-0.14,-1.33 0.28,-2.59 1.67,-3.45c0.49,-0.22 1,-0.37 1.5,-0.47l8.19,-10.12c-2.56,-1.12 -5.31,-1.76 -8.14,-1.75zm-35.85,44.31c-0.61,0.01 -1.22,0.1 -1.85,0.29c-4.08,1.78 -3.71,7.74 -0.85,10.49c0.69,0.62 1.46,1.13 2.26,1.58l7.84,-9.68c-2.41,-1.22 -4.79,-2.72 -7.4,-2.68z" display="inline" enable-background="accumulate" fill="{B}" fill-rule="evenodd" id="path9"/>
    </g>
    </g>
    </svg>
    """
    b64_str = base64.b64encode(svg_code.encode("utf-8")).decode("utf-8")
    return b64_str


def mcpicon(color: str = "#f20a54"):
    svg_code = f"""
    <svg width="70.842949" height="70" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg" version="1.1">

    <g class="layer" display="inline">
    <title>Layer 1</title>
    <path d="m61.51,42.96a33.49,33.49 0 0 0 -33.49,33.49a33.49,33.49 0 0 0 33.49,33.49a33.49,33.49 0 0 0 33.49,-33.49a33.49,33.49 0 0 0 -33.49,-33.49zm0,7.63a25.86,25.86 0 0 1 25.86,25.86a25.86,25.86 0 0 1 -25.86,25.86a25.86,25.86 0 0 1 -25.86,-25.86a25.86,25.86 0 0 1 25.86,-25.86z" display="inline" fill="#084860" id="path1" stroke="#ffffff" stroke-width="0" transform="translate(-26.591699,-41.134689)"/>
    <rect fill="{color}" height="31.05" id="rect1"  width="69.71" x="0.57" y="20.32"/>
    <text fill="#ffffff" font-family="Inter_18pt-SemiBold" font-size="27px" id="text1" stroke="#ffffff" stroke-dashoffset="0" stroke-width="1" transform="scale(1.0837381,0.92273214)" x="5" xml:space="preserve" y="50">
    MCP
    </text>
    </g>
    </svg>
    """
    b64_str = base64.b64encode(svg_code.encode("utf-8")).decode("utf-8")
    return b64_str
