# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-27 13:34:06
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-05 13:04:28

"""MCP Fast 服务模块。

本模块提供基于 FastMCP 框架的 Server-Sent Events (SSE) 服务实现，
用于管理彩票相关的计算任务和查询操作。

主要功能：
    - 提供彩票信息查询工具
    - 提供任务状态监控工具
    - 管理 MCP 服务器的生命周期
    - 动态端口分配和健康检查
"""

import asyncio
import json
import socket
from email import message

import uvicorn
from mcp.server.fastmcp import FastMCP

from . import datamodle as _DM_
from .lotterMange import Lotter_Data, LotteryManager, StatueData, StatusEnum

mcp = FastMCP("LOTTER-MCP-SSE")
server_instance = None
app_state = LotteryManager()
message = "MCP Fast service module loaded."


def WiterSMS(msg):
    global message
    message = msg


def ReadSMS():
    global message
    temp = message
    message = ""  # 读取后清空消息
    return temp


# region resource
@mcp.resource("lottery://system/supported_rules")
def read_lottery_rules() -> str:
    """系统的彩票规则库说明书"""
    try:
        return json.dumps(Lotter_Data, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": "系统规则库解析失败"}, ensure_ascii=False)


@mcp.resource("lottery://filters/current")
def read_lottery_filters() -> str:
    try:
        # app_state.filters 是列表。
        # 加 default=str 是因为：如果列表里装了自定义类的对象，它会自动转成字符串，防止 dumps 崩溃。
        return json.dumps(app_state.filters, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"error": f"解析过滤条件失败: {e}"}, ensure_ascii=False)


@mcp.resource("lottery://results/latest")
def get_latest_result() -> str:
    """获取最新一次计算的最终号码结果"""
    # 1. 拦截未完成状态
    if app_state.status.status != StatusEnum.DONE:
        return json.dumps({"error": "当前没有完成的计算结果可用"}, ensure_ascii=False)

    # 2. 读取列表数据
    try:
        # app_state.latest_result 是列表
        return json.dumps(
            {"result": app_state.results}, ensure_ascii=False, default=str
        )
    except Exception as e:
        return json.dumps({"error": f"序列化结果失败: {e}"}, ensure_ascii=False)


@mcp.resource("lottery://logs/system_log")
def read_system_logs() -> str:
    """读取后台运行日志"""
    try:
        # 因为是 @property，所以【千万不要加括号】
        logs = app_state.get_last_100_lines_of_log
        return json.dumps({"logs": logs}, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"error": f"读取日志失败: {e}"}, ensure_ascii=False)


# endregion


# region tools
@mcp.tool()
def check_calc_status() -> _DM_.TaskStatus:
    """实时获取后台计算任务的进度。

    此工具用于查询当前计算任务的状态。AI 客户端应定期调用此工具
    以监控长时间运行的计算任务的进度。

    返回状态说明：
        - idle: 准备就绪，可以开始新的计算。
        - calculating: 正在努力计算中，请引导用户稍等。
        - done: 计算已完成，现在可以调用获取结果的工具。
        - timeout: 计算时间过长已自动停止。
        - error: 内部逻辑出错。

    Returns:
        dm.TaskStatus: 包含当前状态和已耗时间的任务状态对象。
            - status (str): 当前任务状态
            - elapsed_time (float): 已耗费的时间（秒）

    返回状态说明：
        - status 为 done: 计算已完成。⚠️ 当且仅当状态为 done 时，你才可以去读取 lottery://results/latest 资源获取详细结果！
        - status 为 calculating: 计算正在进行中，请引导用户耐心等待。
        - status 为 idle: 当前没有计算任务在运行，你可以开始一个新的计算。
        - status 为 timeout: 计算任务因超时被自动停止。
        - status 为 error: 计算过程中发生了错误，请检查系统日志获取更多信息， 你可以访问 lottery://logs/system_log 获取程序日志
    """
    current_status = app_state.status
    url = None
    if app_state.status.status == StatusEnum.DONE:
        url = "lottery://results/latest"
    elif app_state.status.status == StatusEnum.ERROR:
        url = "lottery://logs/system_log"
    # 直接返回模型实例，FastMCP 会自动处理序列化
    return _DM_.TaskStatus(
        status=current_status.status,
        elapsed_time=current_status.elapsed_time,
        result_uri=url,
    )


@mcp.tool()
def get_supported_lotteries() -> _DM_.LotteryLibrary:
    """获取系统支持的所有彩票预设及其详细规则。

    此工具返回系统支持的所有彩票类型的完整信息，包括每种彩票的
    球组配置、抽取数量等详细规则。AI 应该在开始任何计算前调用此工具，
    以确保获取正确的彩票名称和参数结构。

    Returns:
        dm.LotteryLibrary: 包含所有支持彩票信息的库对象。
            包含列表中的每个元素包括：
            - name (str): 彩票名称
            - description (str): 彩票描述
            - rules (List[BallGroup]): 球组规则列表
                * group_id (str): 球组标识符
                * range (List[int]): 球号范围 [最小, 最大]
                * count (int): 需要抽取的球数
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
                    _DM_.BallGroup(
                        group_id=group_id, range=info[key], count=info[count_key]
                    )
                )

        # 创建单种彩票模型
        all_lotteries.append(
            _DM_.LotteryInfo(
                name=name,
                description=info.get("description", "无描述"),
                rules=ball_groups,
            )
        )

    # 返回结构化库对象
    return _DM_.LotteryLibrary(lotteries=all_lotteries)


@mcp.tool()
async def start_calculation(request: _DM_.CalculationRequest) -> str:
    """启动一个新的号码计算任务。

    此工具用于开启计算。如果是预设彩票，只需提供名字；
    如果需要自定义规则，请在 custom_rules 中提供球组配置。

    Returns:
        str: 启动结果提示信息。
    """
    # 1. 检查是否已有任务在运行
    if app_state.status.status == StatusEnum.CALCULATING:
        return "⚠️ 当前已有计算任务正在运行，请等待其完成或调用停止工具。"

    rules_to_use = []

    # 2. 判断是自定义彩票还是预设彩票
    if request.custom_rules and len(request.custom_rules) > 0:
        # 【自定义模式】直接使用 AI 传入的自定义规则
        rules_to_use = request.custom_rules
        mode = "自定义规则"
    else:
        # 【预设模式】去 Lotter_Data 中查找
        match_key = None
        for key in Lotter_Data.keys():
            if request.name.strip() in key:
                match_key = key  # 确保名称完全匹配
                break
        if not match_key:
            return (
                f"❌ 错误：找不到名为 '{request.name}' 的预设彩票，且未提供自定义规则。"
            )
        request.name = match_key  # 确保使用正确的预设名称
        info = Lotter_Data[request.name]
        # 解析预设彩票的规则（逻辑同 get_supported_lotteries）
        potential_keys = sorted(
            [k for k in info.keys() if not k.endswith("_K") and k != "description"]
        )
        for key in potential_keys:
            count_key = f"{key}_K"
            if count_key in info:
                group_id = key[1:] if len(key) > 1 and key[0] in ("P", "S") else key
                rules_to_use.append(
                    _DM_.BallGroup(
                        group_id=group_id, range=info[key], count=info[count_key]
                    )
                )
        mode = "预设规则"

    # 3. 更新管理器状态为“计算中”
    app_state.settings = {
        "name": request.name,
        "rules": [
            rule.model_dump() for rule in rules_to_use
        ],  # 存为字典方便后续计算使用
    }
    app_state.timeout = request.timeout
    app_state.status = StatueData(status=StatusEnum.CALCULATING, elapsed_time=0.0)
    app_state.calc_task_running = True

    # 4. 触发后台异步计算任务 (不要用 await 阻塞它)
    asyncio.create_task(
        app_state.background_calculation_worker(request.name, request.timeout)
    )

    return (
        f"✅ 成功以【{mode}】启动了 [{request.name}] 的计算任务！\n"
        f"配置规则数: {len(rules_to_use)} 组\n"
        f"设定超时时间: {request.timeout} 秒\n"
        f"请开始定期调用 check_calc_status 获取最新进度。"
    )


# endregion


# region prompt
@mcp.prompt()
def lottery_workflow() -> str:
    """提供给 AI 的标准彩票计算工作流指南"""
    return """
    你是一个专业的彩票计算助手。当你需要帮用户计算彩票时，请严格遵守以下 SOP (标准操作流程)：
    
    1. 检查库：首先调用 `get_supported_lotteries` 工具，确认用户要求的彩票是否在支持列表中，以及具体的规则参数。
    2. 启动计算：调用 `start_calculation` 工具开启后台计算。
    3. 监控进度：循环调用 `check_calc_status` 工具，每隔 2-3 秒调用一次。
        - 期间请告知用户：“正在努力为您计算中，请稍候...”
    4. 获取结果：当 `check_calc_status` 返回的状态为 `done` 时，立刻读取资源 `lottery://results/latest`。
    5. 展示结果：将从资源中读取到的号码，以美观的排版呈现给最终用户。
    """


# endregion


# region run_mcp_server
async def run_mcp_server():
    """启动 MCP SSE 服务器。

    在独立的异步任务中启动 FastMCP 驱动的 SSE 服务器。自动处理
    端口冲突，当指定端口被占用时会递增尝试其他端口。捕获并优雅
    处理 SSE 连接中断。

    Global:
        server_instance: 全局服务器实例引用，用于后续关闭操作。
        app_state: 应用状态管理器，包含服务器地址和端口配置。

    Note:
        - 日志级别设置为 "critical" 以减少输出噪音
        - ASGI 消息错误视为正常的 SSE 中断
        - 服务关闭时会清理状态

    Raises:
        Exception: 捕获并记录非 SSE 相关的异常，但不会重新抛出。
    """
    WiterSMS("Starting MCP SSE service in a separate thread...")
    for tool in mcp._tool_manager.list_tools():
        print(f"Registered tool: {tool.name}")
    global server_instance
    # 获取 FastMCP 内部生成的 Starlette app
    hostmap = app_state.hostmap
    while is_port_in_use(hostmap.host, hostmap.port):
        hostmap.port += 1
        await asyncio.sleep(0.1)  # 避免过快循环
    WiterSMS(f"Selected port {hostmap.address} for MCP server.")
    app_state.updatehostmap(hostmap)  # 更新全局状态中的端口信息
    try:
        app = mcp.sse_app()
        config = uvicorn.Config(
            app, host=hostmap.host, port=hostmap.port, log_level="critical"
        )
        server_instance = uvicorn.Server(config)
        await server_instance.serve()
    except Exception as e:
        error_msg = str(e)
        if "ASGI message" in error_msg:
            # 这是正常的 SSE 中断，不需要当作错误处理
            WiterSMS("MCP Server: SSE connections closed gracefully.")
        else:
            WiterSMS(f"MCP Server stopped with message: {e}")
    finally:
        # 确保状态被清理
        WiterSMS("MCP Server: Shutdown complete.")


async def stop_mcp_server():
    """优雅关闭 MCP 服务器。

    安全地关闭全局服务器实例，等待其完全停止（最多 3 秒）。
    如果服务器未在运行，则输出相应提示信息。

    Global:
        server_instance: 全局服务器实例引用。

    Note:
        - 最多等待 30 次，每次间隔 0.1 秒（总计 3 秒）
        - 会在控制台输出关闭状态信息
    """
    global server_instance
    if server_instance and server_instance.started:
        WiterSMS("Shutting down MCP server...")
        server_instance.should_exit = True
        for _ in range(30):
            if not server_instance.started:
                break
            await asyncio.sleep(0.1)
        WiterSMS("MCP service successfully detached.")
    else:
        WiterSMS("Server is not running.")


# endregion


# region is_port_in_use
def is_port_in_use(host, port):
    """检查指定的主机和端口是否被占用。

    Args:
        host (str): 要检查的主机地址（如 '127.0.0.1'）。
        port (int): 要检查的端口号。

    Returns:
        bool: 如果端口被占用返回 True，否则返回 False。

    Note:
        使用 TCP 连接尝试来判断端口是否可用。
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        socke_status = s.connect_ex((host, port)) == 0
        return socke_status


# endregion


# region is_server_healthy
async def is_server_healthy():
    """检查 MCP 服务器是否正常运行。

    执行两级健康检查：
    1. 检查内存中的服务器实例状态
    2. 通过网络套接字连接探测服务器可达性

    Global:
        server_instance: 全局服务器实例。
        app_state: 应用状态管理器，包含服务器地址配置。

    Returns:
        bool: 如果服务器健康运行返回 True，否则返回 False。

    Note:
        - 网络探测超时时间为 0.5 秒
        - 任何连接异常都会被记录并返回 False
        - 在线程池中执行网络操作以避免阻塞事件循环
    """
    global server_instance

    # 1. 首先检查内存中的实例状态
    if server_instance is None or not server_instance.started:
        return False

    # 2. 网络探测
    host = app_state.hostmap.host
    port = app_state.hostmap.port

    try:

        def probe():
            with socket.create_connection((host, port), timeout=0.5):
                return True

        # 只要返回了状态码（哪怕是 405 Method Not Allowed 也行），
        # 就说明 HTTP 服务已经起来了
        return await asyncio.to_thread(probe)
    except Exception as ex:
        print(f"Health check failed: {ex}")
        return False


# endregion
