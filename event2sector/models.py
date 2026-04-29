"""数据模型定义"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Direction(Enum):
    """影响方向"""
    BULLISH = "利好"
    BEARISH = "利空"
    NEUTRAL = "中性"
    NEUTRAL_BEARISH = "中性偏空"
    NEUTRAL_BULLISH = "中性偏好"

    @classmethod
    def from_str(cls, s: str) -> "Direction":
        for member in cls:
            if member.value == s:
                return member
        return cls.NEUTRAL


@dataclass
class NewsItem:
    """新闻条目"""
    id: str
    title: str
    content: str
    source: str
    published_at: str
    category: str = ""
    url: str = ""


@dataclass
class Event:
    """从新闻中抽取的事件"""
    news_id: str
    rule_id: str
    title: str
    matched_keywords: list[str] = field(default_factory=list)
    matched_conditions: list[str] = field(default_factory=list)


@dataclass
class SectorImpact:
    """板块影响"""
    sector_name: str
    direction: Direction
    reason: str
    source_event: Event | None = None


@dataclass
class StockHit:
    """命中的个股"""
    code: str
    name: str
    sectors: list[str] = field(default_factory=list)
    related_impacts: list[SectorImpact] = field(default_factory=list)


@dataclass
class DailyReport:
    """日报"""
    date: str
    generated_at: str = ""
    news_items: list[NewsItem] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    sector_impacts: list[SectorImpact] = field(default_factory=list)
    stock_hits: list[StockHit] = field(default_factory=list)
