# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-27 13:34:06
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-31 12:58:41

import uvicorn
from . import datamodle as dm
from typing import Annotated
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
        potential_keys = sorted([k for k in info.keys() if not k.endswith("_K") and k != "description"])
        
        for key in potential_keys:
            count_key = f"{key}_K"
            if count_key in info and isinstance(info[key], list) and len(info[key]) == 2:
                # 提取组名，例如从 "PA" 提取 "A"
                group_id = key[1:] if len(key) > 1 and key[0] in ('P', 'S') else key
                
                # 创建球组模型
                ball_groups.append(dm.BallGroup(
                    group_id=group_id,
                    range=info[key],
                    count=info[count_key]
                ))
        
        # 创建单种彩票模型
        all_lotteries.append(dm.LotteryInfo(
            name=name,
            description=info.get("description", "无描述"),
            rules=ball_groups
        ))
    
    # 返回结构化库对象
    return dm.LotteryLibrary(lotteries=all_lotteries)

async def run_mcp_server():
    print(f"Starting MCP SSE service in a separate thread...")
    for tool in mcp._tool_manager.list_tools():
        print(f"Registered tool: {tool.name} with description: {tool.description}")
    global server_instance
    # 获取 FastMCP 内部生成的 Starlette app
    app = mcp.sse_app()
    host = app_state.server_address["host"]
    port = app_state.server_address["port"]
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server_instance = uvicorn.Server(config)
    await server_instance.serve()