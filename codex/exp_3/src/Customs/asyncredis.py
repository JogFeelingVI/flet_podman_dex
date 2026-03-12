# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-11 03:59:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-11 22:39:23


import json
import time
from typing import Optional, Dict, Any
from upstash_redis.asyncio import Redis


class RedisAPI:
    """
    Upstash Redis 数据库交互接口类
    """

    def __init__(self, url: str, token: str):
        """
        初始化 Redis 客户端
        :param url: Upstash 提供的 REST_URL
        :param token: Upstash 提供的 REST_TOKEN
        """
        self.url = url
        self.token = token
        # 初始化异步 Redis 客户端
        self._client = Redis(url=self.url, token=self.token)
        # 定义 Token 在数据库中的前缀，方便管理
        self._prefix = "auth:token:"
        self._data_prefix = "app:syncdata:"

    async def verify_token(self, user_token: str) -> Dict[str, Any]:
        """
        检测用户提供的 Token 是否有效
        :param user_token: 用户输入的 Token 字符串
        :return: 包含验证结果和数据的字典
        """
        if not user_token or not isinstance(user_token, str):
            return {
                "is_valid": False,
                "msg": "The token cannot be empty or has an incorrect format.",
                "data": None,
            }

        redis_key = f"{self._prefix}{user_token}"

        try:
            # 尝试从数据库获取该 Token 绑定的数据
            user_data = await self._client.get(redis_key)

            if user_data is not None:
                return {
                    "is_valid": True,
                    "msg": "Token verification successful",
                    "data": user_data,  # 这里通常是绑定的 UserID 或用户信息字典
                }
            else:
                return {
                    "is_valid": False,
                    "msg": "The token is invalid or has expired.",
                    "data": None,
                }

        except Exception as e:
            # 捕获网络异常或配置错误，防止程序崩溃
            print(f"[RedisAPI Error] Token verification failed.: {e}")
            return {
                "is_valid": False,
                "msg": f"Database connection error: {e}",
                "data": None,
            }

    async def save_token(
        self, user_token: str, user_data: str, expire_seconds: int = 1800
    ) -> bool:
        """
        (辅助方法) 保存一个 Token 到数据库，并设置过期时间
        :param user_token: 要保存的 Token
        :param user_data: Token 绑定的数据 (如用户ID "user_123")
        :param expire_seconds: 过期时间(秒)，默认 86400秒 (24小时)
        :return: 是否保存成功
        """
        redis_key = f"{self._prefix}{user_token}"
        try:
            await self._client.set(redis_key, user_data, ex=expire_seconds)
            return True
        except Exception as e:
            print(f"[RedisAPI Error] Token saving failed: {e}")
            return False

    async def save_sync_data(self, key_suffix: str, data: dict) -> bool:
        """
        保存字典数据，并自动注入/更新最新时间戳
        :param key_suffix: 数据的唯一标识 (比如 "settings", "user_123_config")
        :param data: 需要保存的 Python 字典
        :return: 是否保存成功
        """
        if not isinstance(data, dict):
            print("[RedisAPI Error] Data must be a dictionary.")
            return False

        data_key = f"{self._data_prefix}{key_suffix}"
        time_key = f"{data_key}:timestamp"

        # 1. 获取当前时间戳 (Unix 秒)
        current_timestamp = int(time.time())

        # 2. 将时间戳也注入到字典内部 (防备不时之需)
        data["_updated_at"] = current_timestamp

        try:
            # 3. 将字典转为 JSON 字符串 (ensure_ascii=False 保证中文不乱码)
            json_str = json.dumps(data, ensure_ascii=False)

            # 4. 双写策略：同时更新数据和时间戳
            # 这里使用了 Redis 的 pipeline(如果有) 或两次 set，Upstash 异步里直接 await 两次即可
            await self._client.set(data_key, json_str)
            await self._client.set(time_key, current_timestamp)

            return True, current_timestamp
        except Exception as e:
            print(f"[RedisAPI Error] Failed to save sync data: {e}")
            return False, current_timestamp

    async def get_sync_data(self, key_suffix: str) -> Optional[dict]:
        """
        读取并解析云端的字典数据
        :param key_suffix: 数据的唯一标识
        :return: 解析后的字典，如果不存在或失败则返回 None
        """
        data_key = f"{self._data_prefix}{key_suffix}"

        try:
            result = await self._client.get(data_key)
            if not result:
                return None

            # Upstash 有时会自动把 JSON 转成 dict，如果返回的是 str，我们需要手动 loads
            if isinstance(result, str):
                return json.loads(result)
            elif isinstance(result, dict):
                return result

        except json.JSONDecodeError:
            print("[RedisAPI Error] The retrieved data is not valid JSON.")
            return None
        except Exception as e:
            print(f"[RedisAPI Error] Failed to read sync data: {e}")
            return None

    async def check_needs_update(self, key_suffix: str, local_timestamp: int) -> bool:
        """
        极速验证：检查云端数据是否比本地数据更新
        :param key_suffix: 数据的唯一标识
        :param local_timestamp: 本地保存的数据时间戳
        :return: True 表示云端有新数据需要拉取，False 表示本地已是最新
        """
        time_key = f"{self._data_prefix}{key_suffix}:timestamp"

        try:
            cloud_timestamp = await self._client.get(time_key)

            # 如果云端没有时间戳，说明还没存过数据，不需要更新
            if not cloud_timestamp:
                return False

            # 对比时间戳
            return int(cloud_timestamp) > int(local_timestamp)

        except Exception as e:
            print(f"[RedisAPI Error] Failed to check timestamp: {e}")
            return False
