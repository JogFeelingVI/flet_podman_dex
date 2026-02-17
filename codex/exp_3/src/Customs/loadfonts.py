# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-02-04 05:32:13
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-06 14:59:29


import requests
import pathlib
import concurrent.futures
import time
from typing import Dict, Optional
from urllib.parse import unquote


# region FontManager
class FontManager:
    """管理并自动生成 Flet 可用的字体映射表"""

    SUPPORTED_EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2"}

    def __init__(self, fonts_subdir: str = "fonts"):
        """
        :param fonts_subdir: 相对于 assets 目录的字体文件夹路径
        """
        self.assets_path = self.__find_assets_dir()
        self.fonts_path = self.assets_path / fonts_subdir
        self.relative_prefix = fonts_subdir
        self.font_map: Dict[str, str] = self._generate_font_map()

    def __find_assets_dir(self):
        """尝试自动获取 assets 目录路径"""
        # 在 Flet 安卓环境中，通常脚本运行在根目录，assets 就在同级
        assets_path = pathlib.Path(__file__).parent.parent
        print(f"debug: {assets_path}")
        return assets_path / "assets"

    def _generate_font_map(self) -> Dict[str, str]:
        fonts = {}
        if not self.fonts_path.exists() or not self.fonts_path.is_dir():
            print(f"Warning: Font directory not found at {self.fonts_path}")
            return fonts

        for file in self.fonts_path.iterdir():
            if file.is_file() and file.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                # 优化 Key 的生成逻辑：
                # 如果是 "Roboto-Bold.ttf"，Key 设为 "Roboto-Bold"
                # 这样可以精确控制不同字重
                font_family_key = file.stem

                # Flet 需要的是相对于 assets 目录的路径
                # 例如: "fonts/Roboto-Bold.ttf"
                fonts[font_family_key] = f"{self.relative_prefix}/{file.name}"

        return fonts

    def get_fonts(self):
        return self.font_map


# endregion


# region FastSourcePicker
class FastSourcePicker:
    def __init__(self):
        self.sources = [
            "https://gitee.com/jogfeelingvi/lotter_resource/raw/main/fonts.json",
            "https://github.com/JogFeelingVI/lotter_resource/raw/refs/heads/main/fonts.json",
        ]
        self.storage_path = self.__storage_path()

    def __storage_path(self):
        storage_temp = pathlib.Path(__file__).parent.parent / "storage/temp"
        storage_temp.mkdir(parents=True, exist_ok=True)
        return storage_temp

    def _fetch_json(self, url):
        """单个请求的任务"""
        try:
            # 设置较短的 timeout，如果 5 秒都没响应直接放弃
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"Successfully retrieved data from the source: {url}")
                return response.json(), url
        except Exception as e:
            print(f"Request to source {url} failed: {e}")
        return None

    def __ObtainResources(self, name: str, filename_raw: str, url: str):
        try:
            # 1. 规范化文件名处理
            # unquote 处理 %20 等 URL 编码，pathlib.Path().name 获取纯文件名
            clean_filename = unquote(pathlib.Path(filename_raw).name)

            # 2. 确保目标目录存在
            font_dir = self.storage_path / "fonts"
            font_dir.mkdir(parents=True, exist_ok=True)

            file_full_path = font_dir / clean_filename

            # 3. 缓存检查：如果文件已存在且大小不为0，直接返回路径，避免重复下载
            if file_full_path.exists() and file_full_path.stat().st_size > 0:
                return {name: str(file_full_path)}

            # 4. 流式下载 (需设置 stream=True)
            # 增加 raise_for_status() 自动检查 404/500 等错误
            with requests.get(url, timeout=10, stream=True) as response:
                response.raise_for_status()

                with open(file_full_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # 过滤掉 keep-alive 新块
                            f.write(chunk)

            # 5. 返回 Flet 映射格式
            # 返回绝对路径的字符串，Flet 可以直接加载
            return {name: str(file_full_path)}
        except Exception as e:
            print(f"Request to source {url} failed: {e}")
        return None

    def __Correction_parameters(self, result) -> dict[str, str]:
        font_map_raw, source_url = result

        # 1. 预处理：生成下载列表
        # 将 url_str 的 fonts.json 替换掉，拿到基础路径
        base_url = str(source_url).replace("/fonts.json", "")

        # 最终返回给 Flet 的映射表
        final_font_map = {}

        # 2. 使用线程池进行并发下载
        # max_workers=5 表示同时下载 5 个文件，通常 5-10 比较合适
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_name = {}

            for name, font_path_suffix in dict(font_map_raw).items():
                # 过滤掉注释或无效配置
                if not str(name).startswith("--"):
                    # 拼接完整的下载地址
                    full_download_url = f"{base_url}{font_path_suffix}"

                    # 提交任务到线程池
                    # __ObtainResources 应该返回 {name: local_path}
                    future = executor.submit(
                        self.__ObtainResources,
                        name,
                        font_path_suffix,
                        full_download_url,
                    )
                    future_to_name[future] = name

            # 3. 收集结果
            for future in concurrent.futures.as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    # 这里的 result 是 __ObtainResources 返回的字典
                    download_result = future.result()
                    if download_result:
                        final_font_map.update(download_result)
                except Exception as e:
                    print(f"字体 {name} 并发下载任务出错: {e}")

        return final_font_map

    def get_fastest_json(self):
        """并行执行，取最快的结果"""
        # 使用线程池并发请求
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.sources)
        ) as executor:
            # 提交所有任务
            future_to_url = {
                executor.submit(self._fetch_json, url): url for url in self.sources
            }

            # 等待第一个任务完成
            # return_when=FIRST_COMPLETED 意味着只要有一个成功就继续
            done, not_done = concurrent.futures.wait(
                future_to_url.keys(),
                timeout=10,  # 总等待限时
                return_when=concurrent.futures.FIRST_COMPLETED,
            )

            # 遍历已完成的任务
            for future in done:
                result = future.result()
                if result:
                    # 只要拿到了有效的 JSON，就尝试取消其他还在进行的任务并返回结果
                    for unfinished in not_done:
                        unfinished.cancel()
                    return self.__Correction_parameters(result)

        print("All sources are inaccessible.")
        return None


# endregion
