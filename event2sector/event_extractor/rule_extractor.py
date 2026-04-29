"""基于规则的事件抽取器"""

from __future__ import annotations

import json
import re
from pathlib import Path

from event2sector.models import Event, NewsItem


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
                events.append(
                    Event(
                        news_id=news.id,
                        rule_id=rule["id"],
                        title=news.title,
                        matched_keywords=matched_kw,
                        matched_conditions=list(set(matched_cond)),
                    )
                )
        return events
