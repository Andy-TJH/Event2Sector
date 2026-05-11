"""事件 → 板块影响 → 个股匹配"""

from __future__ import annotations

import json
from pathlib import Path

from event2sector.models import Direction, Event, SectorImpact, StockHit


class ImpactMapper:
    """根据事件的 event_type 查找板块影响，再匹配个股标签库。"""

    def __init__(self, rules_path: str | Path, stocks_path: str | Path):
        with open(rules_path, "r", encoding="utf-8") as f:
            rules_data = json.load(f)
        # rule_id → sector 定义列表
        self._rule_map: dict[str, list[dict]] = {}
        for rule in rules_data.get("rules", []):
            self._rule_map[rule["id"]] = rule.get("sectors", [])

        with open(stocks_path, "r", encoding="utf-8") as f:
            stocks_data = json.load(f)
        self._stocks: list[dict] = stocks_data.get("stocks", [])

    # ---- 板块影响 ----

    def map_sectors(self, events: list[Event]) -> list[SectorImpact]:
        """将事件列表映射为板块影响列表（同一板块+方向去重，保留首次来源）。"""
        seen: dict[str, SectorImpact] = {}
        for event in events:
            # event_type 对应 rule_id
            sector_defs = self._rule_map.get(event.event_type, [])
            for sd in sector_defs:
                key = f"{sd['name']}_{sd['direction']}"
                if key not in seen:
                    seen[key] = SectorImpact(
                        event_id=event.event_id,
                        sector_name=sd["name"],
                        direction=Direction.from_str(sd["direction"]),
                        impact_score=0.0,
                        reasoning=sd["reason"],
                        rule_id=event.event_type,
                    )
        return list(seen.values())

    # ---- 个股匹配 ----

    def match_stocks(self, impacts: list[SectorImpact]) -> list[StockHit]:
        """根据板块影响匹配个股标签库，返回命中个股列表（每个事件独立一条记录）。"""
        # sector_name → 对应的 SectorImpact 列表
        sector_to_impacts: dict[str, list[SectorImpact]] = {}
        for imp in impacts:
            sector_to_impacts.setdefault(imp.sector_name, []).append(imp)

        hits: list[StockHit] = []
        seen_pairs: set[tuple[str, str]] = set()  # (event_id, stock_code)

        for stock in self._stocks:
            stock_sectors = set(stock["sectors"])
            for imp in impacts:
                if imp.sector_name not in stock_sectors:
                    continue
                pair = (imp.event_id, stock["code"])
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)

                # 找出该股票与本次影响重叠的所有标签
                overlap_tags = list(stock_sectors & {imp.sector_name})

                hits.append(
                    StockHit(
                        event_id=imp.event_id,
                        stock_code=stock["code"],
                        stock_name=stock["name"],
                        matched_sector=imp.sector_name,
                        matched_tags=overlap_tags,
                        reason=imp.reasoning,
                        confidence=1.0,
                    )
                )
        return hits
