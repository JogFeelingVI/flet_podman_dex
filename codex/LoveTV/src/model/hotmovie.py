# @File    : hotmovie.py
# @Time    : 2026/11/08 15:11:08
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : 热门电视剧 电影 动漫


import logging
import re
from dataclasses import dataclass
from typing import Literal

import httpx2

from LoveTV.src.model.timezone import weekday

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.hotmovie")


@dataclass
class QueryParam:
    kind: Literal["movie", "tv"]
    category: Literal["热门", "最近热门", "show"]
    type: Literal["全部", "tv", "show"]


hotMovie = QueryParam("movie", "热门", "全部")
hotTv = QueryParam("tv", "最近热门", "tv")
hotTvShow = QueryParam("tv", "show", "show")


async def fetch_douban_res(
    param=hotMovie,
    limit: int = 20,
    source: str = "direct",
) -> list:
    """
    args limit 默认 20
    args: source
     - direct直连
     - tencent
     - aliyun
    """
    base_urls = {
        "direct": "https://m.douban.com",
        "tencent": "https://m.douban.cmliussss.net",
        "aliyun": "https://m.douban.cmliussss.com",
    }
    base = base_urls.get(source, "https://m.douban.com")
    url = f"{base}/rexxar/api/v2/subject/recent_hot/{param.kind}?start=0&limit={limit}&category={param.category}&type={param.type}"
    # log.info(f"param {param}\n {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": "https://movie.douban.com/",
        "Accept": "application/json, text/plain, */*",
    }
    async with httpx2.AsyncClient(
        verify=False, timeout=15.0, follow_redirects=True
    ) as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
    out = []
    for it in data.get("items", []):
        item_id = it.get("id")
        title = it.get("title")
        if not item_id or not title:
            continue  # 对应 toDoubanMovie() 返回 null 的情况
        pic = it.get("pic") or {}
        cover = pic.get("large") or pic.get("normal") or pic.get("small") or ""
        rating = it.get("rating") or {}
        rate_val = rating.get("value")
        rate = str(rate_val) if rate_val and rate_val > 0 else None
        subtitle = it.get("card_subtitle") or ""
        year_m = re.search(r"(\d{4})", subtitle)
        year = year_m.group(1) if year_m else ""
        ep_info = it.get("episodes_info") or ""
        ep_m = re.search(r"(\d+)集", ep_info)
        total_episodes = int(ep_m.group(1)) if ep_m else -1
        out.append(
            {
                "id": item_id,
                "source": "douban",
                "title": title,
                "source_name": None,
                "year": year,
                "cover": cover,
                "index": 0,
                "total_episodes": total_episodes,
                "play_time": 0,
                "total_time": 0,
                "saveTime": None,  # 客户端用 System.currentTimeMillis()
                "save_time": title,
                "douban_id": item_id,
                "rate": rate,
            }
        )
    return out


async def fetch_bangumi_today() -> list:
    # Bangumi weekday: 1=周一 .. 7=周日
    wday = weekday()
    url = "https://api.bgm.tv/calendar"
    headers = {
        "User-Agent": "Selene-TV/1.0",
        "Accept": "application/json",
    }
    async with httpx2.Client(timeout=15.0, follow_redirects=True) as client:
        r = client.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        for day in data:
            if day.get("weekday", {}).get("id") == wday:
                return day.get("items", [])
    return []
