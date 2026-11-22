# @File    : PlayRecords.py
# @Time    : 2026/11/05 15:47:29
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : xijishoukan

import logging

import httpx2 as httpx

from cashews import cache
from LoveTV.src.model.envpath import app_Video_Cache
from LoveTV.src.model.detailentry import replayCard

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.playrecords")

cache.setup(f"disk://?directory=.{app_Video_Cache()}")


@cache(ttl=5 * 60)
async def load_play_records(base_url: str, cookies: str) -> dict:
    """与 ApiService.getPlayRecords 对齐。返回原始 Map，key 为 'source+id'。"""
    async with httpx.AsyncClient(
        verify=False, timeout=10, follow_redirects=True
    ) as client:
        response = await client.get(
            base_url.rstrip("/") + "/api/playrecords",
            headers={
                "Accept": "application/json",
                "Cookie": cookies,
            },
        )
    response.raise_for_status()
    # log.info(f"recode json {response.json()}")
    return response.json()  # { "source+id": {...}, ... }


def parse_playrecords(raw: dict) -> list:
    """与 ApiService 的解析逻辑对齐:key 切分 + 字段容错默认值 + save_time 倒序。"""
    out = []
    for key, item in raw.items():
        parts = key.split("+")
        source = parts[0] if len(parts) > 1 else ""
        rec_id = parts[1] if len(parts) > 1 else key
        rcard = replayCard.from_dict(
            item, id=item.get("id", rec_id), source=item.get("source", source)
        )
        out.append(rcard)
    return sorted(out, key=lambda r: r.save_time, reverse=True)
