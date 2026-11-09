# @File    : timezone.py
# @Time    : 2026/11/05 09:51:13
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : time zone stamp

from datetime import UTC, datetime, timedelta


def timestamp() -> float:
    now_utc = datetime.now(tz=UTC)
    # 2. 转换为没有时区信息的绝对时间，再提取 timestamp，绕过 DTZ006 警告
    return now_utc.replace(tzinfo=None).timestamp()


def isoneweek(past_timestamp: float) -> bool:
    """判断时间戳是否超过1周完美适配 ruff DTZ002 与 UP017."""
    # 显式传入关键字参数 tz= 并使用现代化别名 UTC
    past_time = datetime.fromtimestamp(past_timestamp, tz=UTC)
    current_time = datetime.now(tz=UTC)

    return (current_time - past_time) < timedelta(weeks=8)


def weekday():
    now_utc = datetime.now(tz=UTC)
    return now_utc.isoweekday()
