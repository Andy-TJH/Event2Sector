"""基于规则的事件抽取器"""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path

from event2sector.models import Event, EventLevel, NewsItem


class RuleBasedExtractor:
    """使用 sector_rules.json 中的关键词 + 条件正则匹配事件。"""

    def __init__(self, rules_path: str | Path):
        rules_path = Path(rules_path)
        with open(rules_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.rules: list[dict] = data.get("rules", [])

    def extract(self, news_items: list[NewsItem]) -> list[Event]:
        """对每条新闻逐条匹配规则，返回命中的事件列表。"""
        events: list[Event] = []
        for news in news_items:
            text = news.title + " " + news.content
            for rule in self.rules:
                matched_kw = [kw for kw in rule["keywords"] if kw in text]
                if not matched_kw:
                    continue
                condition_pattern = rule.get("condition", "")
                matched_cond = re.findall(condition_pattern, text) if condition_pattern else []
                if not matched_cond:
                    continue

                reasoning = (
                    f"命中关键词: {', '.join(matched_kw)}；"
                    f"触发条件: {', '.join(set(matched_cond))}"
                )
                events.append(
                    Event(
                        event_id=str(uuid.uuid4()),
                        news_id=news.id,
                        event_type=rule["id"],
                        event_level=EventLevel.MEDIUM,
                        entities=matched_kw,
                        keywords=matched_kw,
                        confidence=1.0,
                        reasoning=reasoning,
                    )
                )
        return events
