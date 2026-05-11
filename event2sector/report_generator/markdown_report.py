"""Markdown 日报生成器"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from event2sector.models import DailyReport, Direction, SectorImpact, StockHit


class MarkdownReportGenerator:
    """将 DailyReport 渲染为 Markdown 文件。"""

    def render(self, report: DailyReport) -> str:
        lines: list[str] = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines.append(f"# 📰 Event2Sector 盘前日报 — {report.report_date}")
        lines.append("")
        lines.append(f"> 生成时间: {now} ｜ 新闻 {report.news_count} 条 ｜ 事件 {report.event_count} 个")
        lines.append("")

        # ---- 板块影响 ----
        lines.append("## 一、板块影响映射")
        lines.append("")
        if not report.sectors:
            lines.append("_无板块影响。_")
        else:
            lines.append("| 板块 | 方向 | 影响逻辑 | 规则 |")
            lines.append("|------|------|----------|------|")
            for imp in report.sectors:
                icon = _direction_icon(imp.direction)
                score_str = f" ({imp.impact_score:.1f})" if imp.impact_score else ""
                lines.append(
                    f"| {imp.sector_name} | {icon} {imp.direction.value}{score_str} | "
                    f"{imp.reasoning} | {imp.rule_id or '-'} |"
                )
            lines.append("")

        # ---- 相关个股 ----
        lines.append("## 二、相关 A 股个股")
        lines.append("")
        if not report.stock_hits:
            lines.append("_无匹配个股。_")
        else:
            # 按方向分组：需要先找到每只股票对应的 direction
            # 通过 matched_sector 反查 sectors 列表
            sector_dir: dict[str, Direction] = {
                imp.sector_name: imp.direction for imp in report.sectors
            }

            benefit: list[StockHit] = []
            hurt: list[StockHit] = []
            other: list[StockHit] = []

            for sh in report.stock_hits:
                d = sector_dir.get(sh.matched_sector, Direction.NEUTRAL)
                if d == Direction.BENEFIT:
                    benefit.append(sh)
                elif d == Direction.HURT:
                    hurt.append(sh)
                else:
                    other.append(sh)

            if benefit:
                lines.append("### 🟢 利好关注")
                lines.append("")
                lines.append("| 代码 | 名称 | 命中板块 | 标签 | 逻辑 | 置信度 |")
                lines.append("|------|------|----------|------|------|--------|")
                for sh in benefit:
                    lines.append(
                        f"| {sh.stock_code} | {sh.stock_name} | {sh.matched_sector} | "
                        f"{', '.join(sh.matched_tags)} | {sh.reason} | {sh.confidence:.2f} |"
                    )
                lines.append("")

            if hurt:
                lines.append("### 🔴 利空关注")
                lines.append("")
                lines.append("| 代码 | 名称 | 命中板块 | 标签 | 逻辑 | 置信度 |")
                lines.append("|------|------|----------|------|------|--------|")
                for sh in hurt:
                    lines.append(
                        f"| {sh.stock_code} | {sh.stock_name} | {sh.matched_sector} | "
                        f"{', '.join(sh.matched_tags)} | {sh.reason} | {sh.confidence:.2f} |"
                    )
                lines.append("")

            if other:
                lines.append("### ⚪ 中性关注")
                lines.append("")
                lines.append("| 代码 | 名称 | 命中板块 | 标签 |")
                lines.append("|------|------|----------|------|")
                for sh in other:
                    lines.append(
                        f"| {sh.stock_code} | {sh.stock_name} | "
                        f"{sh.matched_sector} | {', '.join(sh.matched_tags)} |"
                    )
                lines.append("")

        # ---- 风险提示 ----
        if report.risk_notes:
            lines.append("## 三、风险提示")
            lines.append("")
            for note in report.risk_notes:
                lines.append(f"- {note}")
            lines.append("")

        # ---- 免责声明 ----
        lines.append("---")
        lines.append("")
        lines.append(
            "*本报告由 Event2Sector 自动生成，仅供研究参考，不构成任何投资建议。*"
        )
        lines.append("")
        return "\n".join(lines)

    def save(self, report: DailyReport, output_dir: str | Path) -> Path:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        content = self.render(report)
        filename = f"report_{report.report_date}.md"
        filepath = output_dir / filename
        filepath.write_text(content, encoding="utf-8")
        return filepath


def _direction_icon(d: Direction) -> str:
    return {
        Direction.BENEFIT: "🟢",
        Direction.HURT: "🔴",
        Direction.NEUTRAL: "⚪",
    }.get(d, "⚪")
