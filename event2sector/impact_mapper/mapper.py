"""事件 → 板块影响 → 个股匹配"""

from __future__ import annotations

import json
from pathlib import Path

from event2sector.models import Direction, Event, SectorImpact, StockHit


class ImpactMapper:
    """根据事件的 rule_id 查找板块影响，再匹配个股标签库。"""

    def __init__(self, rules_path: str | Path, stocks_path: str | Path):
        with open(rules_path, "r", encoding="utf-8") as f:
            rules_data = json.load(f)
        self._rule_map: dict[str, list[dict]] = {}
        for rule in rules_data.get("rules", []):
            self._rule_map[rule["id"]] = rule.get("sectors", [])

        with open(stocks_path, "r", encoding="utf-8") as f:
            stocks_data = json.load(f)
        self._stocks: list[dict] = stocks_data.get("stocks", [])

    # ---- 板块影响 ----

    def map_sectors(self, events: list[Event]) -> list[SectorImpact]:
        """将事件列表映射为板块影响列表（去重合并）。"""
        seen: dict[str, SectorImpact] = {}
        for event in events:
            sector_defs = self._rule_map.get(event.rule_id, [])
            for sd in sector_defs:
                key = f"{sd['name']}_{sd['direction']}"
                if key not in seen:
                    impact = SectorImpact(
                        sector_name=sd["name"],
                        direction=Direction.from_str(sd["direction"]),
                        reason=sd["reason"],
                        source_event=event,
                    )
                    seen[key] = impact
        return list(seen.values())

    # ---- 个股匹配 ----

    def match_stocks(self, impacts: list[SectorImpact]) -> list[StockHit]:
        """根据板块影响匹配个股标签库，返回命中个股列表。"""
        hit_sectors = {imp.sector_name for imp in impacts}
        hits: dict[str, StockHit] = {}
        for stock in self._stocks:
            overlap = set(stock["sectors"]) & hit_sectors
            if not overlap:
                continue
            code = stock["code"]
            if code not in hits:
                hits[code] = StockHit(
                    code=code,
                    name=stock["name"],
                    sectors=stock["sectors"],
                    related_impacts=[],
                )
            for imp in impacts:
                if imp.sector_name in overlap:
                    hits[code].related_impacts.append(imp)
        return list(hits.values())
