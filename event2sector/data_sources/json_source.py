"""从 JSON 文件加载新闻"""

from __future__ import annotations

import json
from pathlib import Path

from event2sector.models import NewsItem


def load_from_json(path: str | Path) -> list[NewsItem]:
    """从 JSON 文件读取新闻列表。

    JSON 格式（字段说明见 models.NewsItem）:
    [
      {
        "id": "...",
        "source": "...",
        "title": "...",
        "content": "...",
        "summary": "...",        # 可选
        "url": "...",            # 可选
        "publish_time": "...",   # 可选，ISO 8601
        "language": "zh",        # 可选，默认 zh
        "region": "CN"           # 可选，默认 CN
      }
    ]
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    items: list[NewsItem] = []
    for entry in raw:
        items.append(
            NewsItem(
                id=entry["id"],
                source=entry.get("source", ""),
                title=entry["title"],
                content=entry.get("content", ""),
                summary=entry.get("summary", ""),
                url=entry.get("url", ""),
                # 兼容旧字段名 published_at
                publish_time=entry.get("publish_time") or entry.get("published_at", ""),
                language=entry.get("language", "zh"),
                region=entry.get("region", "CN"),
            )
        )
    return items
