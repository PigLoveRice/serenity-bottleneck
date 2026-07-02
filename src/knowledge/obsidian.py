# -*- coding: utf-8 -*-
"""Obsidian vault 写入器 —— 候选和证据自动生成 Markdown 笔记。"""

from pathlib import Path
from datetime import datetime

from src.config import settings
from src.types import Candidate, EvidenceItem


VAULT_ROOT = Path(settings.vault_root)

CANDIDATE_TEMPLATE = """---
theme: "{theme_id}"
stock_code: "{stock_code}"
total_score: {total_score}
evidence_grade: "{evidence_grade}"
status: "{status}"
created: "{created_at}"
updated: "{updated_at}"
tags: [瓶颈, {theme_id}, {evidence_grade}]
---

# {stock_name}（{stock_code}）

## 瓶颈定位

{bottleneck_role}

## 评分

| 维度 | 得分 |
|------|------|
| 趋势对齐 | {trend_alignment:.0f}/100 |
| 瓶颈卡位 | {bottleneck_score:.0f}/100 |
| 证据等级 | {evidence_grade} |
| 估值错配 | {valuation_gap:.0f}/100 |
| 拥挤度 | {sentiment_crowd:.0f}/100 |
| **综合** | **{total_score:.1f}/100** |

## 证据摘要

{evidence_summary}

## 风险

{risks}

## 覆盖缺口

{gaps}

## 证据链

{evidence_links}

## 关联

- 主题：[[01-主题/{theme_label}]]
"""

EVIDENCE_TEMPLATE = """---
grade: "{grade}"
source_type: "{source_type}"
candidate: "[[02-候选/{candidate_name}]]"
publisher: "{publisher}"
created: "{created_at}"
tags: [证据, {grade}, {candidate_name}]
---

# {title}

**等级：** {grade}
**来源：** {publisher}（{source_type}）
**关联候选：** [[02-候选/{candidate_name}]]

## 主张

{claim}
"""


def ensure_vault_dirs():
    """确保 vault 目录结构存在。"""
    dirs = ["01-主题", "02-候选", "03-证据", "04-信号", "05-校准", "99-模板"]
    for d in dirs:
        (VAULT_ROOT / d).mkdir(parents=True, exist_ok=True)


def write_candidate_note(candidate: Candidate, theme_label: str,
                          evidence_items: list[EvidenceItem] = None):
    """为候选公司创建/更新 Obsidian 笔记。"""
    ensure_vault_dirs()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    risks = "\n".join(f"- {r}" for r in candidate.risk_flags) if candidate.risk_flags else "- 暂无"
    gaps = "\n".join(f"- {g}" for g in candidate.coverage_gaps) if candidate.coverage_gaps else "- 暂无"

    # 证据链接
    evidence_links = ""
    if evidence_items:
        for e in evidence_items:
            safe_title = e.title[:30].replace("/", "-").replace(":", "")
            evidence_links += f"- [[03-证据/{safe_title}]] ({e.grade})\n"
    else:
        evidence_links = "- 暂无"

    content = CANDIDATE_TEMPLATE.format(
        theme_id=candidate.theme_id,
        stock_code=candidate.stock_code,
        stock_name=candidate.stock_name,
        total_score=candidate.total_score,
        evidence_grade=candidate.evidence_grade,
        status=candidate.status,
        bottleneck_role=candidate.bottleneck_role,
        trend_alignment=candidate.trend_alignment,
        bottleneck_score=candidate.bottleneck_score,
        valuation_gap=candidate.valuation_gap,
        sentiment_crowd=candidate.sentiment_crowd,
        evidence_summary=candidate.evidence_summary or "暂无",
        risks=risks,
        gaps=gaps,
        evidence_links=evidence_links,
        theme_label=theme_label,
        created_at=candidate.created_at or now,
        updated_at=now,
    )

    note_path = VAULT_ROOT / "02-候选" / f"{candidate.stock_name} {candidate.stock_code}.md"
    note_path.write_text(content, encoding="utf-8")
    return note_path


def write_evidence_note(evidence: EvidenceItem, candidate_name: str):
    """为证据条目创建 Obsidian 笔记。"""
    ensure_vault_dirs()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    safe_title = evidence.title[:50].replace("/", "-").replace(":", "").replace("\\", "")

    content = EVIDENCE_TEMPLATE.format(
        grade=evidence.grade,
        source_type=evidence.source_type,
        candidate_name=candidate_name,
        publisher=evidence.publisher or "未知来源",
        title=evidence.title,
        claim=evidence.claim,
        created_at=now,
    )

    note_path = VAULT_ROOT / "03-证据" / f"{safe_title}.md"
    note_path.write_text(content, encoding="utf-8")
    return note_path


def write_theme_note(theme_id: str, theme_label: str, keywords: list[str],
                      bottlenecks: list, candidates_count: int):
    """更新主题笔记。"""
    ensure_vault_dirs()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    keywords_str = ", ".join(keywords[:8])
    bl_text = "\n".join(f"- **{b.name}**（L{b.level}）: {b.bottleneck_reason}" for b in bottlenecks)
    safe_label = theme_label.replace("/", "-").replace("\\", "-")

    content = f"""---
theme_id: "{theme_id}"
updated: "{now}"
tags: [主题, {theme_id}]
---

# {theme_label}

## 关键词

{keywords_str}

## 上次扫描

{now} — 找到 {candidates_count} 个候选

## 瓶颈环节

{bl_text}

## 候选

```dataview
TABLE total_score, evidence_grade, bottleneck_role
FROM "02-候选"
WHERE theme = "{theme_id}" AND status != "killed"
SORT total_score DESC
```
"""

    note_path = VAULT_ROOT / "01-主题" / f"{safe_label}.md"
    note_path.write_text(content, encoding="utf-8")
    return note_path
