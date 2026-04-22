# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-04-03 13:00:00
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-18 01:24:26

"""环境变量管理模块。

本模块集中管理应用程序所需的环境变量和路径配置，
包括 Flet 应用存储路径、临时目录、资产目录等。
"""

import os

from .jackpot_core import randomData


class EnvManager:
    """环境变量管理器。

    提供应用程序所需的环境变量和路径的集中管理。
    """

    def __init__(self):
        """初始化环境变量管理器。"""
        # 获取 Flet 相关的环境变量
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        self.app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
        self.app_assets_dir = os.getenv("FLET_ASSETS_DIR")

        # 构建应用程序特定的路径
        self.jackpot_seting = (
            os.path.join(self.app_data_path, "jackpot_settings.json")
            if self.app_data_path
            else None
        )

        self.upstash_seting = (
            os.path.join(self.app_data_path, "upstash.json")
            if self.app_data_path
            else None
        )

        # 设置 Flet 密钥
        os.environ["FLET_SECRET_KEY"] = randomData.generate_secure_string(16)

    @property
    def data_path(self):
        """获取应用数据路径。"""
        return self.app_data_path

    @property
    def temp_path(self):
        """获取临时路径。"""
        return self.app_temp_path

    @property
    def assets_dir(self):
        """获取资产目录。"""
        return self.app_assets_dir

    @property
    def settings_file(self):
        """获取设置文件路径。"""
        return self.jackpot_seting

    @property
    def upstash_file(self):
        """获取 Upstash 文件路径。"""
        return self.upstash_seting


# 创建全局实例，方便导入使用
env_manager = EnvManager()
