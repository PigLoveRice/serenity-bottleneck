# -*- coding: utf-8 -*-
"""报告生成器 —— 输出 Markdown 格式的瓶颈筛选报告。"""

from datetime import datetime
from pathlib import Path

from src.config import settings
from src.types import ScreenResult, Candidate, SupplyChainLayer


def _render_candidate_table(candidates: list[Candidate]) -> str:
    """渲染候选公司表格。"""
    if not candidates:
        return "暂无候选公司。\n"

    rows = []
    rows.append("| # | 公司 | 代码 | 瓶颈定位 | 趋势 | 卡位 | 证据 | 估值 | 拥挤 | **总分** |")
    rows.append("|---|------|------|---------|------|------|------|------|------|----------|")

    emoji = {0: "🥇", 1: "🥈", 2: "🥉"}

    for i, c in enumerate(candidates):
        rank = emoji.get(i, f"{i+1}")
        rows.append(
            f"| {rank} | **{c.stock_name}** | `{c.stock_code}` "
            f"| {c.bottleneck_role[:40]}... "
            f"| {c.trend_alignment:.0f} | {c.bottleneck_score:.0f} "
            f"| {c.evidence_grade} | {c.valuation_gap:.0f} "
            f"| {c.sentiment_crowd:.0f} "
            f"| **{c.total_score:.1f}** |"
        )

    return "\n".join(rows)


def _render_candidate_details(candidates: list[Candidate]) -> str:
    """渲染每个候选的详细信息。"""
    parts = []

    for c in candidates:
        risk_str = "\n".join(f"  - ⚠️ {r}" for r in c.risk_flags) if c.risk_flags else "  - 暂无"
        gap_str = "\n".join(f"  - 📋 {g}" for g in c.coverage_gaps) if c.coverage_gaps else "  - 暂无"

        parts.append(f"""### {c.stock_name}（{c.stock_code}）

**瓶颈定位：** {c.bottleneck_role}

**评分明细：**

| 维度 | 得分 | 说明 |
|------|------|------|
| 趋势对齐 | {c.trend_alignment:.0f}/100 | 赛道与确定性趋势的对齐程度 |
| 瓶颈卡位 | {c.bottleneck_score:.0f}/100 | 在瓶颈环节中的不可替代性 |
| 证据等级 | {c.evidence_grade} | P0=一手证据 P1=交叉验证 P2=推断 |
| 估值错配 | {c.valuation_gap:.0f}/100 | 高分=被低估 |
| 拥挤度 | {c.sentiment_crowd:.0f}/100 | 低分=未被市场充分定价 |
| **综合** | **{c.total_score:.1f}/100** | |

**证据摘要：** {c.evidence_summary or "暂无"}

**风险标记：**
{risk_str}

**覆盖缺口：**
{gap_str}

""")

    return "\n".join(parts)


def _render_supply_chain(layers: list[SupplyChainLayer]) -> str:
    """渲染供应链层级。"""
    parts = ["### 产业链拆解\n"]
    for layer in layers:
        marker = "🔴 **瓶颈**" if layer.is_bottleneck else "🟢"
        part = f"**L{layer.level}: {layer.name}** {marker}\n  {layer.description}"
        if layer.is_bottleneck:
            part += f"\n  > 瓶颈原因：{layer.bottleneck_reason}"
        parts.append(part)
        parts.append("")
    return "\n".join(parts)


def generate_report(result: ScreenResult) -> str:
    """生成完整的 Markdown 报告。

    Returns:
        Markdown 文本。
    """
    report = f"""# 🔍 Serenity 产业链投研

**主题：** {result.theme.label}
**运行时间：** {result.run_at}
**运行 ID：** `{result.run_id}`

---

## 方法论提醒

本报告基于 Serenity 产业链瓶颈方法论（Bottleneck Theory）生成。
核心逻辑：从产业趋势出发 → 逆向拆解供应链 → 定位不可替代的瓶颈环节 → 映射 A 股候选公司。

⚠️ 本报告是研究候选，**不构成投资建议**。所有评分基于公开信息和 LLM 推理，存在信息缺口。

---

{_render_supply_chain(result.supply_chain)}

---

## 候选公司评分

**核心逻辑：** 产业趋势 → 逆推供应链 → 定位瓶颈环节 → 映射 A 股候选。

{_render_candidate_table(result.candidates)}

---

## 候选详情

{_render_candidate_details(result.candidates)}

---

## 覆盖缺口声明

以下信息缺口可能影响评分准确性：
- 最新的季报/年报数据（需手动验证）
- 实际产能利用率和良率数据（非公开信息）
- 客户定点/订单的精确状态（依赖公告披露）
- 券商研报的深度分析（当前未接入研报系统）

---

*生成方式：Serenity Bottleneck Agent (Phase 3)*
*方法论：产业链瓶颈逆推 (Bottleneck Theory)*
"""

    return report


def save_report(report: str, theme_id: str) -> Path:
    """保存报告到 runs/ 目录。

    Returns:
        报告文件路径。
    """
    runs_dir = Path(settings.runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"screen_{theme_id}_{timestamp}.md"
    path = runs_dir / filename
    path.write_text(report, encoding="utf-8")

    return path
