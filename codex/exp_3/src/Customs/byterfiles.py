# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-21 11:05:27
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-23 02:59:05
import base64
from pathlib import Path
from typing import Any, Optional, Union

import msgpack


class BinaryConverter:
    """使用 MsgPack 处理对象与二进制/Base64 之间的转换"""

    @staticmethod
    def save(path: Union[str, Path], obj: Any) -> bool:
        """
        将对象序列化并保存到文件
        :return: 成功返回 True，失败返回 False
        """
        try:
            with open(path, "wb") as f:
                # use_bin_type=True 确保跨语言兼容性
                msgpack.pack(obj, f, use_bin_type=True)
            return True
        except Exception:
            return False

    @staticmethod
    def load(path: Union[str, Path], default: Any = None) -> Any:
        """
        从文件读取并反序列化对象
        :param default: 如果读取失败（如文件不存在、格式错误），返回的默认值
        """
        try:
            with open(path, "rb") as f:
                # raw=False 会自动将 bytes 转换为 utf-8 字符串
                return msgpack.unpack(f, raw=False)
        except Exception:
            return default

    @staticmethod
    def to_base64(obj: Any) -> Optional[str]:
        """将对象转换为 Base64 字符串"""
        try:
            binary_data = msgpack.packb(obj, use_bin_type=True)
            return base64.b64encode(binary_data).decode("utf-8")
        except Exception:
            return None

    @staticmethod
    def from_base64(b64_str: str, default: Any = None) -> Any:
        """将 Base64 字符串还原为对象"""
        try:
            if not b64_str:
                return default
            binary_data = base64.b64decode(b64_str.encode("utf-8"))
            return msgpack.unpackb(binary_data, raw=False)
        except Exception:
            return default
