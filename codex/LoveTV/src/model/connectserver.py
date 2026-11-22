# @File    : connectserver.py
# @Time    : 2026/11/14 07:15:14
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : 练习网络系统的服务

# @File    : connectserver.py
# @Time    : 2026/11/14 07:15:14
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : 练习网络系统的服务

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import urllib.parse
from collections import Counter
from collections.abc import Awaitable, Callable
from typing import Any

import httpx2
from cashews import cache

# ---------- 日志与配置 ----------
LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.ConnectServer")

SERVER_URL = "http://127.0.0.1:3000"
COOKIES = ""

M3U8_PROXY_URL = ""
CDN_PREFIX = ""
SELENE_SOURCE_API = ""
TMDB_API_KEY = ""
TIMEOUT = 15.0
SSL_VERIFY = True

DOUBAN_BASE = "https://m.douban.com"
FILTERED_TYPE_NAMES = frozenset({"伦理片", "福利", "里番"})

cache.setup("mem://")

ProgressCallback = Callable[[int, str], Awaitable[None]]


def configureClient(
    server: str,
    cookies: str,
    source_key: str = "",
) -> None:
    """更新服务端地址、Cookie 与可选的源站详情 API。"""
    global SERVER_URL, COOKIES, SELENE_SOURCE_API, M3U8_PROXY_URL
    if server and server.strip():
        SERVER_URL = server.strip().rstrip("/")
        # M3U8_PROXY_URL = SERVER_URL + "/api/proxy?url="
    if cookies is not None:
        COOKIES = cookies.strip()
    if source_key:
        SELENE_SOURCE_API = fetch_source_api(source_key)


def fetch_source_api(source_key: str | None = None) -> str | None:
    """从 /api/search/resources 获取指定 source 的 api base（httpx2/httpx 通用）。"""
    headers = {"Accept": "application/json", "Cookie": COOKIES}
    try:
        with httpx2.Client(verify=False, timeout=15.0) as client:
            r = client.get(f"{SERVER_URL}/api/search/resources", headers=headers)
            r.raise_for_status()
            resources = r.json()  # list of {key, name, api, ...}
    except Exception as e:
        return None

    if source_key:
        for res in resources:
            if res.get("key") == source_key:
                return res.get("api")
    # 未指定时返回第一个可用源的 api
    for res in resources:
        if res.get("api"):
            return res.get("api")
    return None


# ---------- 异步 HTTP 工具 ----------
async def http_get(
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    timeout: float = TIMEOUT,
) -> tuple[int, str]:
    try:
        async with httpx2.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            verify=SSL_VERIFY,
        ) as client:
            resp = await client.get(url, headers=headers or {}, params=params)
            return resp.status_code, resp.text
    except httpx2.HTTPError as exc:
        log.warning("GET %s 失败: %s", url, exc)
        return 0, ""


async def http_post_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str] | None = None,
    timeout: float = TIMEOUT,
) -> int:
    try:
        async with httpx2.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            verify=SSL_VERIFY,
        ) as client:
            resp = await client.post(url, json=payload, headers=headers or {})
            return resp.status_code
    except httpx2.HTTPError as exc:
        log.warning("POST %s 失败: %s", url, exc)
        return 0


def _server_headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    headers: dict[str, str] = {}
    if COOKIES:
        headers["Cookie"] = COOKIES
    if extra:
        headers.update(extra)
    return headers


# ---------- 通用进度总线 ----------
class ProgressBus:
    """可插拔进度上报：支持注册多个监听器，步骤可自由扩展。"""

    def __init__(self) -> None:
        self._listeners: list[ProgressCallback] = []

    def on(self, cb: ProgressCallback) -> None:
        if cb not in self._listeners:
            self._listeners.append(cb)

    async def report(self, pct: int, task: str) -> None:
        clamped = max(0, min(100, pct))
        for cb in list(self._listeners):
            try:
                await cb(clamped, task)
            except Exception:
                log.exception("进度回调执行异常: %s", task)


# ---------- 搜索与详情匹配逻辑 ----------
def _source_key(item: dict[str, Any]) -> str:
    source = str(item.get("source") or "").strip()
    vid = str(item.get("id") or "").strip()
    return f"{source}+{vid}" if source and vid else ""


def _normalize_search_item(raw: dict[str, Any]) -> dict[str, Any]:
    item = dict(raw)
    if not item.get("id") and item.get("vod_id") is not None:
        item["id"] = str(item["vod_id"])
    if not item.get("title") and item.get("vod_name"):
        item["title"] = str(item["vod_name"])
    if not item.get("year") and item.get("vod_year") is not None:
        item["year"] = str(item["vod_year"])
    if not item.get("typeName") and item.get("type_name"):
        item["typeName"] = str(item["type_name"])
    if not item.get("doubanId") and item.get("douban_id") is not None:
        item["doubanId"] = str(item["douban_id"])
    return item


def accept(entry_type: str, result: dict[str, Any], entry: dict[str, Any]) -> bool:
    entry_did = str(entry.get("doubanId") or "").strip()
    result_did = str(result.get("doubanId") or "").strip()

    if entry_type == "douban":
        if entry_did and result_did:
            return result_did == entry_did
        if entry_did and not result_did:
            # 部分下游源站不返回 doubanId，降级按标题+年份校验
            pass
        else:
            return False

    entry_title = str(entry.get("title") or "").strip().casefold()
    result_title = str(result.get("title") or "").strip().casefold()
    if not entry_title or result_title != entry_title:
        return False

    entry_year = str(entry.get("year") or "").strip()
    result_year = str(result.get("year") or "").strip()
    if entry_year and result_year:
        return result_year == entry_year
    return True


def content_filter(type_name: str) -> bool:
    return type_name.strip() in FILTERED_TYPE_NAMES


def dedup(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in results:
        key = _source_key(item)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


async def downstream_search(query: str) -> list[dict[str, Any]]:
    if not SERVER_URL or not query.strip():
        return []
    status, body = await http_get(
        f"{SERVER_URL}/api/search",
        headers=_server_headers({"Accept": "application/json"}),
        params={"q": query.strip()},
    )
    if status != 200 or not body:
        log.warning("搜索接口请求失败: status=%s, query=%s", status, query)
        return []
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        log.warning("搜索结果 JSON 解析失败: %s", exc)
        return []

    if isinstance(data, dict):
        items = data.get("results") or data.get("data") or data.get("list") or []
    elif isinstance(data, list):
        items = data
    else:
        return []

    return [_normalize_search_item(x) for x in items if isinstance(x, dict)]


async def get_detail_by_source_id(source: str, vid: str) -> dict[str, Any] | None:
    if not source or not vid:
        return None
    if SERVER_URL:
        status, body = await http_get(
            f"{SERVER_URL}/api/detail",
            headers=_server_headers({"Accept": "application/json"}),
            params={"source": source, "id": vid},
        )
        if status == 200 and body:
            try:
                data = json.loads(body)
                detail = data.get("data") if isinstance(data, dict) else None
                target = detail if isinstance(detail, dict) else data
                if isinstance(target, dict):
                    item = _normalize_search_item(target)
                    item.setdefault("source", source)
                    item.setdefault("id", vid)
                    eps = _extract_episodes_from_payload(target, source)
                    if eps:
                        item["episodes"] = eps
                    return item
            except json.JSONDecodeError as exc:
                log.warning("详情 JSON 解析失败 (%s+%s): %s", source, vid, exc)

    episodes = await fetch_detail_episodes(source, vid)
    if not episodes:
        return None
    return {
        "source": source,
        "id": vid,
        "episodes": episodes,
    }


def tier2_douban_id(results: list[dict[str, Any]]) -> str | None:
    counts = Counter(
        str(r.get("doubanId")).strip() for r in results if r.get("doubanId")
    )
    for did, count in counts.items():
        if count >= 2:
            return did
    return None


@cache(ttl="6h", key="douban:details:{douban_id}")
async def _fetch_douban_subject(douban_id: str) -> dict[str, Any]:
    url = f"{DOUBAN_BASE}/rexxar/api/v2/subject/{urllib.parse.quote(douban_id)}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://movie.douban.com/",
        "Accept": "application/json",
    }
    status, body = await http_get(url, headers=headers)
    if status != 200:
        raise ValueError(f"豆瓣接口返回异常状态码: {status}")
    data = json.loads(body)
    if not isinstance(data, dict):
        raise ValueError("豆瓣接口返回结构异常")
    return data


async def get_douban_details(douban_id: str) -> dict[str, Any] | None:
    if not douban_id:
        return None
    try:
        return await _fetch_douban_subject(douban_id)
    except (ValueError, json.JSONDecodeError) as exc:
        log.warning("获取豆瓣详情失败 (%s): %s", douban_id, exc)
        return None


# ---------- 播放解析与记录 ----------
def _is_valid_http_url(value: Any) -> bool:
    return isinstance(value, str) and value.startswith(("http://", "https://"))


def _extract_url_list(raw_episodes: Any) -> list[str]:
    if not isinstance(raw_episodes, list):
        return []
    urls: list[str] = []
    for ep in raw_episodes:
        if _is_valid_http_url(ep):
            urls.append(ep)
        elif isinstance(ep, dict):
            candidate = ep.get("url") or ep.get("playUrl") or ep.get("play_url")
            if _is_valid_http_url(candidate):
                urls.append(str(candidate))
    return urls


def _parse_play_url(play_url: str, play_from: str, source: str) -> list[str]:
    if not play_url:
        return []
    url_groups = [g.strip() for g in play_url.split("$$$") if g.strip()]
    if not url_groups:
        return []

    target_group = url_groups[0]
    if play_from and source:
        from_groups = [f.strip() for f in play_from.split("$$$")]
        for idx, name in enumerate(from_groups):
            if idx < len(url_groups) and (name == source or source in name):
                target_group = url_groups[idx]
                break

    episodes: list[str] = []
    for seg in target_group.split("#"):
        item = seg.strip()
        if not item:
            continue
        if "$" in item:
            item = item.split("$", 1)[-1].strip()
        if _is_valid_http_url(item):
            episodes.append(item)
    return episodes


def _extract_episodes_from_payload(data: Any, source: str) -> list[str]:
    if not isinstance(data, dict):
        return []

    inner = data.get("data")
    if isinstance(inner, dict):
        from_inner = _extract_episodes_from_payload(inner, source)
        if from_inner:
            return from_inner

    direct = _extract_url_list(data.get("episodes"))
    if direct:
        return direct

    play_url = data.get("vod_play_url") or data.get("vodPlayUrl") or ""
    play_from = data.get("vod_play_from") or data.get("vodPlayFrom") or ""
    if play_url:
        return _parse_play_url(str(play_url), str(play_from), source)

    lst = data.get("list") or []
    if isinstance(lst, list) and lst and isinstance(lst[0], dict):
        first = lst[0]
        return _extract_episodes_from_payload(first, source)
    return []


async def fetch_detail_episodes(source: str, item_id: str) -> list[str]:
    if not item_id:
        return []

    # 1. 优先请求主服务端 /api/detail
    if SERVER_URL:
        status, body = await http_get(
            f"{SERVER_URL}/api/detail",
            headers=_server_headers({"Accept": "application/json"}),
            params={"source": source, "id": item_id},
        )
        if status == 200 and body:
            try:
                eps = _extract_episodes_from_payload(json.loads(body), source)
                if eps:
                    return eps
            except json.JSONDecodeError as exc:
                log.warning("服务端详情解析失败 (%s+%s): %s", source, item_id, exc)

    # 2. 备选：独立源站 MacCMS 接口
    if SELENE_SOURCE_API:
        status, body = await http_get(
            SELENE_SOURCE_API,
            headers={"Accept": "application/json"},
            params={"ac": "videolist", "ids": item_id},
        )
        if status == 200 and body:
            try:
                return _extract_episodes_from_payload(json.loads(body), source)
            except json.JSONDecodeError as exc:
                log.warning("源站剧集解析失败 (%s+%s): %s", source, item_id, exc)

    return []


async def normalize_episodes(src: dict[str, Any]) -> dict[str, Any]:
    eps = src.get("episodes") or []
    valid_eps = _extract_url_list(eps)
    if (
        valid_eps
        and len(valid_eps) == len(eps)
        and all(isinstance(x, str) for x in eps)
    ):
        return src

    if valid_eps:
        updated = dict(src)
        updated["episodes"] = valid_eps
        return updated

    urls = await fetch_detail_episodes(
        str(src.get("source") or ""),
        str(src.get("id") or ""),
    )
    updated = dict(src)
    updated["episodes"] = urls
    return updated


def build_play_url(
    raw_url: str,
    proxy_url: str | None = None,
    cdn_prefix: str | None = None,
) -> str:
    if not _is_valid_http_url(raw_url):
        raise ValueError(f"无效的播放地址: {raw_url!r}")

    active_proxy = M3U8_PROXY_URL if proxy_url is None else proxy_url
    # log.info(f"active_proxy {active_proxy}")
    active_cdn = CDN_PREFIX if cdn_prefix is None else cdn_prefix

    url = raw_url
    if active_proxy:
        url = active_proxy + urllib.parse.quote(raw_url, safe="")
    if active_cdn:
        encoded = urllib.parse.quote(url, safe=":/?&=%")
        url = f"{active_cdn.rstrip('/')}/{encoded}"
    return url


def resume_for_episode(record: dict[str, Any] | None, episode_index: int) -> int:
    if not record:
        return 0
    rec_index = int(record.get("index") or 1) - 1
    if rec_index == episode_index:
        return max(0, int(record.get("play_time") or 0)) * 1000
    return 0


def build_player_launch(
    entry: dict[str, Any],
    state: dict[str, Any],
    episode_index: int = 0,
) -> dict[str, Any]:
    selected_key = state.get("selectedSourceKey")
    src = next(
        (s for s in state.get("sources", []) if _source_key(s) == selected_key),
        None,
    )
    episodes = src.get("episodes") if src else None
    if not src or not episodes:
        raise ValueError("无可用播放源")

    ep_index = max(0, min(episode_index, len(episodes) - 1))
    record = state.get("playRecords", {}).get(selected_key)
    start_ms = resume_for_episode(record, ep_index)
    duration_ms = max(0, int((record or {}).get("total_time") or 45 * 60)) * 1000

    return {
        "title": entry.get("title") or src.get("title") or "",
        "sources": state["sources"],
        "selectedSourceKey": selected_key,
        "episodeIndex": ep_index,
        "startPositionMs": start_ms,
        "durationMs": duration_ms,
    }


async def save_play_record(
    source_key: str,
    src: dict[str, Any],
    title: str,
    episode_index: int,
    position_ms: int,
    duration_ms: int,
) -> None:
    if not SERVER_URL:
        return
    body = {
        "key": source_key,
        "record": {
            "id": src["id"],
            "source": src["source"],
            "title": title,
            "source_name": src.get("source_name", src.get("sourceName", "")),
            "year": src.get("year", ""),
            "cover": src.get("cover", src.get("poster", "")),
            "index": episode_index + 1,
            "total_episodes": len(src.get("episodes", [])),
            "play_time": max(0, position_ms // 1000),
            "total_time": max(0, duration_ms // 1000),
            "save_time": int(time.time() * 1000),
            "search_title": src.get("search_title", src.get("searchTitle", title)),
        },
    }
    status = await http_post_json(
        f"{SERVER_URL}/api/playrecords",
        payload=body,
        headers=_server_headers({"Content-Type": "application/json"}),
    )
    log.info("进度上报状态: %s", status)


# ---------- 详情流程（进度可插拔） ----------
async def detail_screen_flow(
    entry: dict[str, Any],
    bus: ProgressBus | None = None,
) -> dict[str, Any]:
    bus = bus or ProgressBus()
    report = bus.report

    entry_type = str(entry.get("type") or "")
    need_details = entry_type in {"douban", "bangumi", "history", "search_aggregate"}
    state: dict[str, Any] = {
        "rawResults": [],
        "sourcesComplete": False,
        "detailsLoading": need_details,
        "details": None,
        "detailsError": None,
        "bangumiDetails": None,
        "tmdbTrigger": None,
        "tmdbArt": None,
        "tmdbRef": None,
        "tier2Target": None,
        "playRecords": {},
        "favoriteKeys": set(),
        "sources": [],
        "selectedSourceKey": None,
    }

    async def search_sources() -> None:
        await report(5, "正在搜索播放源...")
        query = entry.get("searchTitle") or entry.get("title") or ""
        if query:
            results = await downstream_search(str(query))
            await report(15, "搜索结果累积中...")
            accepted = [
                r
                for r in results
                if accept(entry_type, r, entry)
                and not content_filter(str(r.get("typeName") or ""))
            ]
            if accepted:
                state["rawResults"] = dedup(state["rawResults"] + accepted)

        # 若 entry 本身指定了 source+id（如 history 或从搜索结果进入），确保它在候选列表中
        source, vid = entry.get("source"), entry.get("id")
        if source and vid:
            target_key = f"{source}+{vid}"
            has_key = any(_source_key(r) == target_key for r in state["rawResults"])
            if not has_key:
                await report(20, "按 source+id 补齐指定源...")
                entry_eps = _extract_url_list(entry.get("episodes"))
                if entry_eps:
                    merged = _normalize_search_item(entry)
                    merged["episodes"] = entry_eps
                    state["rawResults"] = dedup(state["rawResults"] + [merged])
                else:
                    detail = await get_detail_by_source_id(str(source), str(vid))
                    if detail:
                        state["rawResults"] = dedup(state["rawResults"] + [detail])
                    elif entry.get("title"):
                        state["rawResults"] = dedup(
                            state["rawResults"] + [_normalize_search_item(entry)]
                        )

        state["sourcesComplete"] = True
        await report(30, f"播放源搜索完成，共 {len(state['rawResults'])} 个源")

    async def fetch_details() -> None:
        if not need_details:
            return
        await report(45, "正在解析详情元数据...")
        douban_id = entry.get("doubanId") or tier2_douban_id(state["rawResults"])
        if douban_id:
            state["tier2Target"] = str(douban_id)
            details = await get_douban_details(str(douban_id))
            if details is not None:
                state["details"] = details
            else:
                state["detailsError"] = f"未能获取豆瓣详情 ({douban_id})"
        state["detailsLoading"] = False
        await report(75, "详情元数据加载完成")

    async def fetch_user_data() -> None:
        await report(80, "正在拉取播放记录与收藏...")
        if not SERVER_URL:
            await report(85, "未配置服务地址，跳过用户数据")
            return

        records_status, records_body = await http_get(
            f"{SERVER_URL}/api/playrecords",
            headers=_server_headers({"Accept": "application/json"}),
            timeout=5.0,
        )
        if records_status == 200 and records_body:
            try:
                data = json.loads(records_body)
                if isinstance(data, dict):
                    state["playRecords"] = data
            except json.JSONDecodeError:
                log.warning("播放记录 JSON 解析失败")

        fav_status, fav_body = await http_get(
            f"{SERVER_URL}/api/favorites",
            headers=_server_headers({"Accept": "application/json"}),
            timeout=5.0,
        )
        if fav_status == 200 and fav_body:
            try:
                data = json.loads(fav_body)
                if isinstance(data, dict):
                    state["favoriteKeys"] = set(data.keys())
                elif isinstance(data, list):
                    state["favoriteKeys"] = {str(x) for x in data}
            except json.JSONDecodeError:
                log.warning("收藏列表 JSON 解析失败")

        await report(85, "用户数据就绪")

    async def derive_sources() -> None:
        await report(88, "正在派生展示源列表...")
        raw = state["rawResults"]
        if entry_type == "history":
            entry_key = f"{entry.get('source')}+{entry.get('id')}"
            group = sorted(
                raw,
                key=lambda r: _source_key(r) == entry_key,
                reverse=True,
            )
            displayed = group if state["sourcesComplete"] else []
        else:
            displayed = raw

        normalized = await asyncio.gather(
            *(normalize_episodes(s) for s in dedup(displayed))
        )
        state["sources"] = list(normalized)
        await report(90, f"展示源就绪，共 {len(state['sources'])} 个")

    async def select_default_source() -> None:
        await report(92, "正在选定默认播放源...")
        sources = state["sources"]
        if not sources:
            await report(95, "无可用播放源")
            return

        playable = [s for s in sources if s.get("episodes")]
        pool = playable or sources

        current = state["selectedSourceKey"]
        still_valid = current is not None and any(
            _source_key(s) == current for s in pool
        )
        if not still_valid:
            pick = None
            if entry.get("source") and entry.get("id"):
                ek = f"{entry.get('source')}+{entry.get('id')}"
                pick = next((s for s in pool if _source_key(s) == ek), None)

            if pick is None and state["playRecords"]:

                def _save_ts(src_item: dict[str, Any]) -> int:
                    rec = state["playRecords"].get(_source_key(src_item)) or {}
                    return int(rec.get("saveTime") or rec.get("save_time") or 0)

                pick = max(pool, key=_save_ts)

            if pick is None:
                pick = pool[0]

            state["selectedSourceKey"] = _source_key(pick)

        await report(95, f"默认源: {state['selectedSourceKey']}")

    await search_sources()
    await asyncio.gather(fetch_details(), fetch_user_data())
    await derive_sources()
    await select_default_source()
    await report(100, "加载完成")
    return state
