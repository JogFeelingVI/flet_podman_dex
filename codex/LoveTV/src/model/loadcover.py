# @File    : loadcover.py
# @Time    : 2026/11/07 17:34:16
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : CDN -> Download -> images

from __future__ import annotations

import logging
import re
import urllib.parse
from pathlib import Path

import httpx2 as httpx

from LoveTV.src.model.envpath import app_cache_path
from LoveTV.src.storage import load_auth_config

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.Player")

# ---------- 1. 输入：一条播放记录 ----------
PLAY_RECORD = {
    "id": "16803",
    "source": "dyttzy",
    "title": "怪诞小镇 第一季",
    "source_name": "电影天堂资源",
    "year": "2012",
    "cover": "https://img.dytt-tupian.com/upload/vod/20250307-1/77a5dccab7bbab580483288307454f9f.jpg",
    "index": 7,
    "total_episodes": 20,
    "play_time": 455,
    "total_time": 1377,
    "save_time": 1793942030477,
    "search_title": "怪诞小镇 第一季",
}

# ---------- 2. 配置（对应 AppDataService SharedPreferences） ----------
# SERVER_URL = "http://127.0.0.1:3000"          # 自建服务器地址（未登录可留空）
# COOKIES = ""                                   # 登录后保存的 cookie 字符串
DOUBAN_IMAGE_SOURCE = "official_cdn"  # douban 图片源：official_cdn / cdn_tencent / cdn_aliyun / server_proxy
BANGUMI_IMAGE_SOURCE = "official"  # bangumi 图片源：official / server_proxy

DOUBAN_REGEX = re.compile(r"img\d+\.doubanio\.com")
BANGUMI_HOSTS = ("lain.bgm.tv", "bgm.tv")


def get_image_url_sync(original_url: str, server, cookie) -> str:
    """对应 util/ImageUrl.kt :: getImageUrlSync"""
    if not original_url:
        return original_url

    # 豆瓣
    if "doubanio.com" in original_url:
        key = DOUBAN_IMAGE_SOURCE
        if key == "server_proxy":
            if server:
                encoded = urllib.parse.quote(original_url, safe="")
                return f"{server.rstrip('/')}/api/image-proxy?url={encoded}"
            return original_url
        if key == "official_cdn":
            return DOUBAN_REGEX.sub("img3.doubanio.com", original_url)
        if key == "cdn_tencent":
            return DOUBAN_REGEX.sub("img.doubanio.cmliussss.net", original_url)
        if key == "cdn_aliyun":
            return DOUBAN_REGEX.sub("img.doubanio.cmliussss.com", original_url)
        return original_url

    # Bangumi
    if any(h in original_url for h in BANGUMI_HOSTS):
        if BANGUMI_IMAGE_SOURCE == "server_proxy" and server:
            encoded = urllib.parse.quote(original_url, safe="")
            return f"{server.rstrip('/')}/api/image-proxy?url={encoded}"
        return original_url

    # 其它
    return original_url


def is_self_hosted(url: str, server) -> bool:
    """对应 ImageHeaderInterceptor: 请求 host 命中已登录的自托管服务 host"""
    if not server:
        return False
    from urllib.parse import urlparse

    return urlparse(url).hostname == urlparse(server).hostname


def build_headers(url: str, server, cookie) -> dict:
    """对应 ImageHeaderInterceptor"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": "https://movie.douban.com/",
    }
    if is_self_hosted(url, server) and cookie:
        headers["Cookie"] = cookie
    return headers


async def fetch_image_cached(url: str, path: Path, headers) -> bytes:
    """Download an image once per app session and reuse its bytes afterward."""
    # if url not in _IMAGE_CACHE:
    #     async with httpx.AsyncClient(timeout=20) as client:
    #         response = await client.get(url)
    #         response.raise_for_status()
    #         _IMAGE_CACHE[url] = response.content
    # return _IMAGE_CACHE[url]
    async with httpx.AsyncClient(
        timeout=10, follow_redirects=True, verify=False, headers=headers
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        image_bytes = response.content
        path.write_bytes(image_bytes)
    return image_bytes


async def cacha_cover(cover: str, raw_source: str, raw_id: id) -> str:
    """
    缓冲系统图片
    """
    cache_img = app_cache_path() / f"{raw_source}_{raw_id}.image"
    if cache_img.is_file():
        cached_bytes = cache_img.read_bytes()
        return cached_bytes
    else:
        server, cookies = load_auth_config()
        recover_url = get_image_url_sync(
            original_url=cover, server=server, cookie=cookies
        )
        headers = build_headers(recover_url, server, cookies)
        cached_bytes = await fetch_image_cached(recover_url, cache_img, headers)
    return cached_bytes
