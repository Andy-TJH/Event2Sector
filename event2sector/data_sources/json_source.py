"""从 JSON 文件加载新闻"""

from __future__ import annotations

import json
from pathlib import Path

from event2sector.models import NewsItem


def load_from_json(path: str | Path) -> list[NewsItem]:
    """从 JSON 文件读取新闻列表。

    JSON 格式:
    [
      {
        "id": "...",
        "title": "...",
        "content": "...",
        "source": "...",
        "published_at": "...",
        "category": "...",
        "url": ""
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
                title=entry["title"],
                content=entry["content"],
                source=entry.get("source", ""),
                published_at=entry.get("published_at", ""),
                category=entry.get("category", ""),
                url=entry.get("url", ""),
            )
        )
    return items
