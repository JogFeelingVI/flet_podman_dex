# @File    : detail_entry.py
# @Time    : 2026/11/19 09:03:25
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : videoInfo -> detail_entry

import re
from dataclasses import dataclass, asdict, fields

# {
# 	'title': '天黑请回家第二季',
# 	'source_name': '魔都资源',
# 	'year': '2021',
# 	'cover': 'https://www.mdzypic.com/upload/vod/20240702-1/9576e806e4b567cdc29850aec1b2ab17.jpg',
# 	'index': 5,
# 	'total_episodes': 10,
# 	'play_time': 650,
# 	'total_time': 2740,
# 	'save_time': 1782459473129,
# 	'search_title': ''
# }


@dataclass
class replayCard:
    """ """

    title: str
    cover: str
    index: int
    total_episodes: int
    save_time: int
    play_time: int
    total_time: int = 1
    search_title: str = ""
    source_name: str | None = None
    year: str = "1949"
    # 这两项在你的示例数据中未出现，设为可选默认值（如必传可去掉 = "" 并移到最上面）
    id: str = ""
    source: str = ""

    def to_dict(self) -> dict[str, None]:
        """转换为 dict"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, int], **overrides) -> "replayCard":
        valid_keys = {f.name for f in fields(cls)}
        # 先把 data 和额外传入的 overrides 合并，同名键后者覆盖前者，不会冲突
        merged = {**data, **overrides}
        filtered_data = {k: v for k, v in merged.items() if k in valid_keys}
        return cls(**filtered_data)


# {
# 	'id': '36689621',
# 	'title': '今天是太阳雨',
# 	'pic': {
# 		'large': 'https://img3.doubanio.com/view/photo/m_ratio_poster/public/p2935903589.jpg',
# 		'normal': 'https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2935903589.jpg'
# 	},
# 	'rating': {
# 		'count': 67735,
# 		'max': 10,
# 		'star_count': 4.0,
# 		'value': 8.0
# 	},
# 	'uri': 'douban://douban.com/tv/36689621',
# 	'card_subtitle': '2026 / 中国大陆 / 剧情 爱情 / 猫的树 / 杨超越 董思成',
# 	'is_new': False,
# 	'episodes_info': '24集全',
# 	'type': 'tv'
# }


@dataclass
class videoCard:
    id: str
    title: str
    cover: str
    douban_id: str
    rate: float
    play_time: int = 0
    save_time: int = 0
    source: str = ""
    source_name: str | None = None
    year: str = "1949"
    total_episodes: int = 0
    index: int = 0
    total_time: int = 1
    card_subtitle: str = ""
    is_new: bool = False
    type: str = "tv"

    def to_dict(self) -> dict[str, None]:
        """转换为 dict"""
        return asdict(self)

    @classmethod
    def from_douban(cls, data: dict) -> "videoCard":
        # 1. 从 uri ('douban://douban.com/tv/36689621') 拆分出 source
        uri = data.get("uri") or ""
        source = uri.split("://", 1)[0] if "://" in uri else ""
        # 2. 提取封面
        pic = data.get("pic") or {}
        cover = pic.get("large") or pic.get("normal") or ""
        # 3. 提取评分
        rating = data.get("rating") or {}
        rate = float(rating.get("value") or 0.0)
        # 4. 从 card_subtitle 提取年份
        subtitle = data.get("card_subtitle") or ""
        year_match = re.match(r"^\s*(\d{4})", subtitle)
        year = year_match.group(1) if year_match else "1949"
        # 5. 从 episodes_info 提取集数
        ep_info = data.get("episodes_info") or ""
        ep_match = re.search(r"(\d+)", ep_info)
        total_episodes = int(ep_match.group(1)) if ep_match else 0
        douban_id = str(data.get("id", ""))
        card_subtitle = str(data.get("card_subtitle", ""))
        is_new = bool(data.get("is_new", False))
        video_type = str(data.get("type", ""))
        return cls(
            id=douban_id,
            source=source,
            douban_id=douban_id,
            title=data.get("title", ""),
            cover=cover,
            rate=rate,
            year=year,
            total_episodes=total_episodes,
            card_subtitle=card_subtitle,
            is_new=is_new,
            type=video_type,
        )


# ---------- VideoInfo 定义 ----------
@dataclass
class VideoInfo:
    title: str
    cover: str
    year: str
    source: str
    id: str
    search_title: str = ""
    douban_id: str | None = None
    bangumi_id: str | None = None

    def to_dict(self) -> dict[str, None]:
        """转换为 dict"""
        return asdict(self)

    def toDetailEntry(self):
        return detail_entry_for(self)

    @classmethod
    def from_dict(cls, data: dict[str, None]) -> "VideoInfo":
        """从 dict 还原为 VideoInfo 实例"""
        valid_keys = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)


# ---------- DetailEntry 定义 ----------


@dataclass
class Douban:
    douban_id: str
    title: str
    poster: str
    year: str


@dataclass
class Bangumi:
    bangumi_id: int
    title: str
    poster: str
    year: str


@dataclass
class History:
    source: str
    id: str
    search_title: str
    title: str
    poster: str
    year: str


@dataclass
class SearchAggregate:
    agg: object  # AggregatedSearchResult 占位


type DetailEntry = Douban | Bangumi | History | SearchAggregate


def detail_entry_for(video: VideoInfo) -> DetailEntry:
    """按 VideoInfo 字段分流入口 doubanId > bangumiId > 否则按 source+id 当作历史/收藏。"""
    douban_id = video.douban_id
    bangumi_id = video.bangumi_id
    if douban_id is not None:
        return Douban(
            douban_id=douban_id, title=video.title, poster=video.cover, year=video.year
        )
    if bangumi_id is not None:
        return Bangumi(
            bangum_id=bangumi_id, title=video.title, poster=video.cover, year=video.year
        )
    return History(
        source=video.source,
        id=video.id,
        search_title=video.search_title if video.search_title else video.title,
        title=video.title,
        poster=video.cover,
        year=video.year,
    )
