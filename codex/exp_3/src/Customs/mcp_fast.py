# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-27 13:34:06
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-02 14:14:13

import socket
import uvicorn
import asyncio
from . import datamodle as dm
from typing import List
from mcp.server.fastmcp import FastMCP
from .lotterMange import LotteryManager, Lotter_Data


mcp = FastMCP(f"LOTTER-MCP-SSE")
server_instance = None
app_state = LotteryManager()


@mcp.tool()
def check_calc_status() -> dm.TaskStatus:
    """
    实时获取后台计算任务的进度。

    返回状态说明：
    - idle: 准备就绪，可以开始。
    - calculating: 正在努力计算中，请引导用户稍等。
    - done: 计算已完成，现在可以调用获取结果的工具。
    - timeout: 计算时间过长已自动停止。
    - error: 内部逻辑出错。
    """
    current_status = getattr(app_state, "status", "idle")
    current_elapsed = getattr(app_state, "elapsed_time", 0.0)

    # 直接返回模型实例，FastMCP 会自动处理序列化
    return dm.TaskStatus(status=current_status, elapsed_time=current_elapsed)


@mcp.tool()
def get_supported_lotteries() -> dm.LotteryLibrary:
    """
    获取系统支持的所有彩票预设及其详细规则。
    AI 应该在开始任何计算前调用此工具，以确保获取正确的彩票名称和参数结构。
    """
    all_lotteries = []

    # 动态解析你的 Lotter_Data 字典
    for name, info in Lotter_Data.items():
        ball_groups = []

        # 寻找所有规则对 (例如 PA 和 PA_K)
        potential_keys = sorted(
            [k for k in info.keys() if not k.endswith("_K") and k != "description"]
        )

        for key in potential_keys:
            count_key = f"{key}_K"
            if (
                count_key in info
                and isinstance(info[key], list)
                and len(info[key]) == 2
            ):
                # 提取组名，例如从 "PA" 提取 "A"
                group_id = key[1:] if len(key) > 1 and key[0] in ("P", "S") else key

                # 创建球组模型
                ball_groups.append(
                    dm.BallGroup(
                        group_id=group_id, range=info[key], count=info[count_key]
                    )
                )

        # 创建单种彩票模型
        all_lotteries.append(
            dm.LotteryInfo(
                name=name,
                description=info.get("description", "无描述"),
                rules=ball_groups,
            )
        )

    # 返回结构化库对象
    return dm.LotteryLibrary(lotteries=all_lotteries)


async def run_mcp_server():
    print(f"Starting MCP SSE service in a separate thread...")
    for tool in mcp._tool_manager.list_tools():
        print(f"Registered tool: {tool.name}")
    global server_instance
    # 获取 FastMCP 内部生成的 Starlette app
    host = app_state.server_address["host"]
    port = app_state.server_address["port"]
    
    while is_port_in_use(host,port):
        port += 1
        app_state.setting_port(port)
        await asyncio.sleep(0.1)  # 避免过快循环
    try:
        app = mcp.sse_app()
        config = uvicorn.Config(app, host=host, port=port, log_level="critical")
        server_instance = uvicorn.Server(config)
        await server_instance.serve()
        print(f"MCP server address: {app_state.server_address['address']}")
    except Exception as e:
        error_msg = str(e)
        if "ASGI message" in error_msg:
            # 这是正常的 SSE 中断，不需要当作错误处理
            print("MCP Server: SSE connections closed gracefully.")
        else:
            print(f"MCP Server stopped with message: {e}")
    finally:
        # 确保状态被清理
        print("MCP Server: Shutdown complete.")


async def stop_mcp_server():
    """优雅关闭服务"""
    global server_instance
    if server_instance and server_instance.started:
        print("Shutting down MCP server...")
        server_instance.should_exit = True
        for _ in range(30):
            if not server_instance.started:
                break
            await asyncio.sleep(0.1)
        print("MCP service successfully detached.")
    else:
        print("Server is not running.")

def is_port_in_use(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        socke_status = s.connect_ex((host, port)) == 0
        return socke_status

async def is_server_healthy():
    """使用 requests 判断服务是否正常运行"""
    global server_instance

    # 1. 首先检查内存中的实例状态
    if server_instance is None or not server_instance.started:
        return False

    # 2. 网络探测
    host = app_state.server_address["host"]
    port = app_state.server_address["port"]

    try:
        def probe():
            with socket.create_connection((host, port), timeout=0.5):
                return True

        # 只要返回了状态码（哪怕是 405 Method Not Allowed 也行），
        # 就说明 HTTP 服务已经起来了
        return await asyncio.to_thread(probe)
    except Exception as e:
        return False
