# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-28 01:18:11
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-02 05:28:49

import traceback
import datetime
import logging
import sys
import os

# 1. 配置日志格式
# %(asctime)s 自动处理 datetime
# %(levelname)s 自动处理级别名称
# %(message)s 自动处理消息内容
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout)  # 确保输出到标准输出，方便 adb logcat 查看
    ],
)

logr = logging.getLogger('flet_core')
# loger = logging.getLogger(__name__)


# regiong loginfo
class LogInfo:
    def __init__(self, show_time: bool = True):
        # 使用常量定义格式，避免实例属性被误改
        self.show_time = show_time
        self.logpath = None
        self.log_format = (
            "[{time}] {level}: {message}" if show_time else "{level}: {message}"
        )

    def set_log_path(self, path: str):
        """
        设置日志文件的保存路径
        :param path: 完整的路径字符串，例如 /data/user/0/.../app_log.txt
        """
        self.info(f'set log path: {path}')
        try:
            # 自动创建不存在的目录
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            self.logpath = path
            self.info(f"The log path has been set to: {path}")
        except Exception as er:
            self.error(f"Failed to set log path: {er}")

    def __emit(self, level: str, message: str, ex: Exception = None):
        """内部统一处理日志输出"""
        # 1. 处理时间
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = str(message)
        if ex is not None:
            # 获取完整堆栈并拼接到消息后面
            error_stack = traceback.format_exc()
            full_message = (
                f"{full_message}\nException: {ex}\nStack Trace:\n{error_stack}"
            )

        # 3. 格式化最终字符串 (使用关键字参数修复原有 bug)
        log_str = self.log_format.format(
            time=now, level=level.upper(), message=full_message
        )

        # 4. 实际执行打印 (或者写入文件)
        if self.logpath:
            try:
                # 使用 'a' 模式表示追加 (append)
                # encoding="utf-8" 确保安卓端中文不乱码
                with open(self.logpath, "a", encoding="utf-8") as f:
                    f.write(log_str + "\n")
            except Exception as e:
                # 如果写文件失败，仅在控制台提示，不要让 App 崩溃
                print(f"Unable to write to log file: {e}")
        print(log_str)
        return log_str

    def info(self, message: str):
        return self.__emit("info", message)

    def debug(self, message: str):
        return self.__emit("debug", message)

    def error(self, message: str, ex: Exception = None):
        """支持传入 Exception 对象以自动记录堆栈"""
        return self.__emit("error", message, ex=ex)


# endregion

# logr = LogInfo(show_time=True)
