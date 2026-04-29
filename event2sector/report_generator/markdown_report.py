"""Markdown 日报生成器"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from event2sector.models import DailyReport, Direction


class MarkdownReportGenerator:
    """将 DailyReport 渲染为 Markdown 文件。"""

    def render(self, report: DailyReport) -> str:
        lines: list[str] = []
        lines.append(f"# 📰 Event2Sector 盘前日报 — {report.date}")
        lines.append("")
        lines.append(f"> 生成时间: {report.generated_at}")
        lines.append("")

        # ---- 事件摘要 ----
        lines.append("## 一、隔夜事件摘要")
        lines.append("")
        if not report.events:
            lines.append("_未识别到可映射事件。_")
        else:
            for i, evt in enumerate(report.events, 1):
                lines.append(
                    f"{i}. **{evt.title}**  "
                )
                lines.append(
                    f"   关键词: {', '.join(evt.matched_keywords)} | "
                    f"触发条件: {', '.join(evt.matched_conditions)}"
                )
            lines.append("")

        # ---- 板块影响 ----
        lines.append("## 二、板块影响映射")
        lines.append("")
        if not report.sector_impacts:
            lines.append("_无板块影响。_")
        else:
            lines.append("| 板块 | 方向 | 逻辑 | 来源事件 |")
            lines.append("|------|------|------|----------|")
            for imp in report.sector_impacts:
                icon = _direction_icon(imp.direction)
                event_title = imp.source_event.title if imp.source_event else "-"
                lines.append(
                    f"| {imp.sector_name} | {icon} {imp.direction.value} | "
                    f"{imp.reason} | {event_title} |"
                )
            lines.append("")

        # ---- 相关个股 ----
        lines.append("## 三、相关 A 股个股")
        lines.append("")
        if not report.stock_hits:
            lines.append("_无匹配个股。_")
        else:
            # 按利好/利空分组展示
            bullish_stocks: list = []
            bearish_stocks: list = []
            other_stocks: list = []
            for sh in report.stock_hits:
                directions = {imp.direction for imp in sh.related_impacts}
                if Direction.BULLISH in directions:
                    bullish_stocks.append(sh)
                elif Direction.BEARISH in directions:
                    bearish_stocks.append(sh)
                else:
                    other_stocks.append(sh)

            if bullish_stocks:
                lines.append("### 🟢 利好关注")
                lines.append("")
                lines.append("| 代码 | 名称 | 所属板块 | 影响逻辑 |")
                lines.append("|------|------|----------|----------|")
                for sh in bullish_stocks:
                    reasons = "; ".join(
                        dict.fromkeys(
                            f"{imp.sector_name}: {imp.reason}"
                            for imp in sh.related_impacts
                            if imp.direction == Direction.BULLISH
                        )
                    )
                    lines.append(
                        f"| {sh.code} | {sh.name} | "
                        f"{', '.join(sh.sectors)} | {reasons} |"
                    )
                lines.append("")

            if bearish_stocks:
                lines.append("### 🔴 利空关注")
                lines.append("")
                lines.append("| 代码 | 名称 | 所属板块 | 影响逻辑 |")
                lines.append("|------|------|----------|----------|")
                for sh in bearish_stocks:
                    reasons = "; ".join(
                        dict.fromkeys(
                            f"{imp.sector_name}: {imp.reason}"
                            for imp in sh.related_impacts
                            if imp.direction == Direction.BEARISH
                        )
                    )
                    lines.append(
                        f"| {sh.code} | {sh.name} | "
                        f"{', '.join(sh.sectors)} | {reasons} |"
                    )
                lines.append("")

            if other_stocks:
                lines.append("### ⚪ 其他关注")
                lines.append("")
                lines.append("| 代码 | 名称 | 所属板块 |")
                lines.append("|------|------|----------|")
                for sh in other_stocks:
                    lines.append(
                        f"| {sh.code} | {sh.name} | {', '.join(sh.sectors)} |"
                    )
                lines.append("")

        # ---- 免责声明 ----
        lines.append("---")
        lines.append("")
        lines.append(
            "*本报告由 Event2Sector 自动生成，仅供参考，不构成投资建议。*"
        )
        lines.append("")
        return "\n".join(lines)

    def save(self, report: DailyReport, output_dir: str | Path) -> Path:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        content = self.render(report)
        filename = f"report_{report.date}.md"
        filepath = output_dir / filename
        filepath.write_text(content, encoding="utf-8")
        return filepath


def _direction_icon(d: Direction) -> str:
    return {
        Direction.BULLISH: "🟢",
        Direction.BEARISH: "🔴",
        Direction.NEUTRAL: "⚪",
        Direction.NEUTRAL_BEARISH: "🟡",
        Direction.NEUTRAL_BULLISH: "🟡",
    }.get(d, "⚪")
