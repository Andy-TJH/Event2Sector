"""数据模型定义"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# 枚举
# ---------------------------------------------------------------------------

class Direction(Enum):
    """板块影响方向"""
    BENEFIT = "benefit"   # 利好
    HURT = "hurt"         # 利空
    NEUTRAL = "neutral"   # 中性

    @classmethod
    def from_str(cls, s: str) -> "Direction":
        """支持英文值及中文别名。"""
        _alias: dict[str, Direction] = {
            "benefit": cls.BENEFIT,
            "利好": cls.BENEFIT,
            "hurt": cls.HURT,
            "利空": cls.HURT,
            "neutral": cls.NEUTRAL,
            "中性": cls.NEUTRAL,
        }
        return _alias.get(s.lower(), cls.NEUTRAL)


class EventLevel(Enum):
    """事件重要程度"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ---------------------------------------------------------------------------
# 核心数据模型
# ---------------------------------------------------------------------------

@dataclass
class NewsItem:
    """新闻条目"""
    id: str                          # 唯一标识
    source: str                      # 来源媒体
    title: str                       # 标题
    content: str                     # 正文（完整内容）
    summary: str = ""                # 摘要（可由 LLM 生成或原始摘要字段）
    url: str = ""                    # 原文链接
    publish_time: str = ""           # 发布时间，ISO 8601 格式
    language: str = "zh"             # 语言代码，如 zh / en
    region: str = "CN"               # 地区代码，如 CN / US / EU


@dataclass
class Event:
    """从新闻中抽取的结构化事件"""
    event_id: str                              # 事件唯一 ID
    news_id: str                               # 来源新闻 ID
    event_type: str                            # 事件类型，如 oil_price / fed_rate / chip_policy
    event_level: EventLevel = EventLevel.MEDIUM  # 事件重要程度
    entities: list[str] = field(default_factory=list)    # 涉及实体，如 ["OPEC", "布伦特原油"]
    keywords: list[str] = field(default_factory=list)    # 命中关键词
    confidence: float = 1.0                    # 置信度 [0, 1]
    reasoning: str = ""                        # 抽取依据（规则描述或 LLM 推理链）


@dataclass
class SectorImpact:
    """板块影响"""
    event_id: str                    # 来源事件 ID
    sector_name: str                 # 板块名称
    direction: Direction             # 影响方向：benefit / hurt / neutral
    impact_score: float = 0.0        # 影响强度 [0, 1]，0 表示未评分
    reasoning: str = ""              # 影响逻辑说明
    rule_id: str = ""                # 触发规则 ID（规则模式下填写，LLM 模式可为空）


@dataclass
class StockHit:
    """命中的个股"""
    event_id: str                                          # 来源事件 ID
    stock_code: str                                        # 股票代码
    stock_name: str                                        # 股票名称
    matched_sector: str = ""                               # 命中的板块名称
    matched_tags: list[str] = field(default_factory=list)  # 命中的标签列表
    reason: str = ""                                       # 命中原因说明
    confidence: float = 1.0                                # 置信度 [0, 1]


@dataclass
class DailyReport:
    """盘前日报"""
    report_date: str                                              # 报告日期，YYYY-MM-DD
    news_count: int = 0                                           # 输入新闻总数
    event_count: int = 0                                          # 识别事件总数
    sectors: list[SectorImpact] = field(default_factory=list)     # 板块影响列表
    stock_hits: list[StockHit] = field(default_factory=list)      # 命中个股列表
    risk_notes: list[str] = field(default_factory=list)           # 风险提示（如规则覆盖不足、置信度低等）
