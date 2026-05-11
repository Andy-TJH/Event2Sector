"""命令行入口"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from event2sector.data_sources import load_from_json
from event2sector.event_extractor import RuleBasedExtractor
from event2sector.impact_mapper import ImpactMapper
from event2sector.models import DailyReport
from event2sector.report_generator import MarkdownReportGenerator

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RULES = PROJECT_ROOT / "configs" / "sector_rules.json"
DEFAULT_STOCKS = PROJECT_ROOT / "configs" / "stock_tags.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "reports"


def run_pipeline(
    news_path: str | Path,
    rules_path: str | Path = DEFAULT_RULES,
    stocks_path: str | Path = DEFAULT_STOCKS,
    output_dir: str | Path = DEFAULT_OUTPUT,
    report_date: str | None = None,
) -> Path:
    """执行完整流水线：新闻 → 事件 → 板块 → 个股 → 报告。"""
    # 1. 加载新闻
    news_items = load_from_json(news_path)
    print(f"[1/4] 加载新闻 {len(news_items)} 条")

    # 2. 事件抽取
    extractor = RuleBasedExtractor(rules_path)
    events = extractor.extract(news_items)
    print(f"[2/4] 识别事件 {len(events)} 个")

    # 3. 板块 & 个股映射
    mapper = ImpactMapper(rules_path, stocks_path)
    sector_impacts = mapper.map_sectors(events)
    stock_hits = mapper.match_stocks(sector_impacts)
    print(f"[3/4] 映射板块 {len(sector_impacts)} 个，命中个股 {len(stock_hits)} 只")

    # 4. 生成报告
    date_str = report_date or datetime.now().strftime("%Y-%m-%d")
    report = DailyReport(
        report_date=date_str,
        news_count=len(news_items),
        event_count=len(events),
        sectors=sector_impacts,
        stock_hits=stock_hits,
        risk_notes=[],
    )
    generator = MarkdownReportGenerator()
    filepath = generator.save(report, output_dir)
    print(f"[4/4] 报告已生成 → {filepath}")
    return filepath


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Event2Sector: 隔夜事件 → A股板块映射 → 盘前报告"
    )
    parser.add_argument(
        "news", help="新闻 JSON 文件路径（如 examples/sample_news.json）"
    )
    parser.add_argument(
        "--rules", default=str(DEFAULT_RULES), help="板块规则文件路径"
    )
    parser.add_argument(
        "--stocks", default=str(DEFAULT_STOCKS), help="个股标签库路径"
    )
    parser.add_argument(
        "--output", default=str(DEFAULT_OUTPUT), help="报告输出目录"
    )
    parser.add_argument(
        "--date", default=None, help="报告日期（默认今天，格式 YYYY-MM-DD）"
    )
    args = parser.parse_args()

    run_pipeline(
        news_path=args.news,
        rules_path=args.rules,
        stocks_path=args.stocks,
        output_dir=args.output,
        report_date=args.date,
    )


if __name__ == "__main__":
    main()
