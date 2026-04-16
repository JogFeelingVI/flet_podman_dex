# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-31 00:56:56
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-05 12:53:28

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# region LotteryInfo
class BallGroup(BaseModel):
    """
    描述单组球的抽取规则
    """

    group_id: str = Field(..., description="球组标识，如 A, B, 红球, 蓝球等")
    range: List[int] = Field(..., description="号码范围，格式为 [最小值, 最大值]")
    count: int = Field(..., description="该组需要抽取的球数")


class CalculationRequest(BaseModel):
    name: str = Field(
        ...,
        description="彩票名称。如果是预设的（如'🔴双色球'），可以直接填；如果是自定义的，请起个新名字。",
    )
    custom_rules: Optional[List[BallGroup]] = Field(
        None,
        description="如果是预设彩票，此项可为空。如果是新彩票，请提供具体的球组规则列表。",
    )
    timeout: int = Field(60, description="超时时间")


class LotteryInfo(BaseModel):
    """
    单种彩票的完整信息
    """

    name: str = Field(..., description="彩票的唯一名称")
    description: str = Field(..., description="彩票的描述信息")
    rules: List[BallGroup] = Field(..., description="该彩票包含的所有球组规则")


class LotteryLibrary(BaseModel):
    """
    系统支持的所有彩票库
    """

    lotteries: List[LotteryInfo]
    can_customize: bool = Field(True, description="是否支持用户提供自定义参数进行计算")


# endregion


# region TaskStatus
class TaskStatus(BaseModel):
    """
    任务状态数据结构：描述当前后台计算的实时进展。
    """

    status: Literal["idle", "calculating", "done", "timeout", "error", "stopped"] = (
        Field(..., description="任务的当前生命周期阶段")
    )
    elapsed_time: float = Field(..., description="从计算开始到现在所经过的时间（秒）")
    result_uri: Optional[str] = Field(
        None, description="当状态为 done 时，读取详细结果的资源 URI"
    )


# endregion


def main():
    print("Hello, World!")


if __name__ == "__main__":
    main()
