# -*- coding: utf-8 -*-
"""校准引擎 —— 追踪预测，评估准确性。"""

import json
import logging
from datetime import datetime
from pathlib import Path

from src.config import settings
from src.knowledge.database import get_db

logger = logging.getLogger(__name__)

VAULT_CAL = Path(settings.vault_root) / "05-校准"


def snapshot_predictions(theme_id: str = None):
    """对当前候选做一次预测快照，记录到 calibration 表。

    每个候选的 current_score 就是"预测置信度"。
    """
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    today = datetime.now().strftime("%Y-%m-%d")

    where = "status='candidate'"
    params = []
    if theme_id:
        where += " AND theme_id=?"
        params.append(theme_id)

    rows = db.execute(
        f"SELECT id, stock_name, stock_code, total_score FROM candidates WHERE {where}",
        params
    ).fetchall()

    count = 0
    for r in rows:
        # 检查今天是否已经记录过
        existing = db.execute(
            "SELECT id FROM calibration WHERE candidate_id=? AND prediction_date=?",
            (r["id"], today)
        ).fetchone()
        if existing:
            continue

        import uuid
        db.execute(
            "INSERT INTO calibration (id, candidate_id, prediction_date, target_date, predicted_score) "
            "VALUES (?,?,?,?,?)",
            (uuid.uuid4().hex[:10], r["id"], today,
             today, r["total_score"])
        )
        count += 1

    db.commit()
    db.close()
    logger.info(f"校准快照: {count} 个候选")
    return count


def evaluate_predictions(theme_id: str = None):
    """评估历史预测的准确性。

    Returns:
        dict with summary stats
    """
    db = get_db()

    where = "c.status='candidate'"
    params = []
    if theme_id:
        where += " AND c.theme_id=?"
        params.append(theme_id)

    # 获取有多次记录的候选
    rows = db.execute(f"""
        SELECT c.stock_name, c.stock_code, c.total_score as current_score,
               COUNT(cal.id) as snapshots,
               AVG(cal.predicted_score) as avg_predicted,
               MIN(cal.predicted_score) as min_predicted,
               MAX(cal.predicted_score) as max_predicted
        FROM candidates c
        LEFT JOIN calibration cal ON cal.candidate_id = c.id
        WHERE {where}
        GROUP BY c.id
        HAVING COUNT(cal.id) >= 1
        ORDER BY c.total_score DESC
    """, params).fetchall()

    # 计算简单校准指标
    # Brier Score 简化版：(predicted/100 - actual/100)^2 的平均值
    # 由于没有 actual 数据，只做趋势分析

    vault_note = _build_calibration_note(rows, theme_id)
    db.close()

    # 写入 Obsidian vault
    VAULT_CAL.mkdir(parents=True, exist_ok=True)
    note_path = VAULT_CAL / f"校准报告_{datetime.now().strftime('%Y%m%d')}.md"
    note_path.write_text(vault_note, encoding="utf-8")

    return vault_note, note_path


def _build_calibration_note(rows, theme_id: str = None) -> str:
    """生成校准报告 Markdown。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    title = f"校准报告 — {theme_id or '全部主题'}"
    
    lines = [
        f"---",
        f"type: calibration",
        f"date: {now}",
        f"theme: {theme_id or 'all'}",
        f"---",
        f"",
        f"# {title}",
        f"",
        f"生成时间：{now}",
        f"",
        f"## 候选评分趋势",
        f"",
        f"| 公司 | 当前评分 | 快照次数 | 平均预测 | 最低 | 最高 | 趋势 |",
        f"|------|---------|---------|---------|------|------|------|",
    ]

    for r in rows:
        current = r["current_score"] or 0
        avg = r["avg_predicted"] or current
        trend = "📈" if current > avg + 3 else ("📉" if current < avg - 3 else "➡️")
        lines.append(
            f"| {r['stock_name']} | {current:.1f} | {r['snapshots']} | "
            f"{avg:.1f} | {r['min_predicted'] or current:.1f} | "
            f"{r['max_predicted'] or current:.1f} | {trend} |"
        )

    lines += [
        "",
        "## 说明",
        "",
        "- 校准尚处于数据积累阶段。当候选记录达到 10+ 次快照后，将启用 Brier Score 评估。",
        "- 当前阶段关注评分稳定性：同一候选多次评分的标准差越小越好。",
        "- 若某候选评分持续下降，可能在评分覆盖缺口——需要补充证据。",
    ]

    return "\n".join(lines)


def cmd_calibrate(theme_id: str = None):
    """CLI 入口：运行校准。"""
    print("📊 校准引擎")
    print()

    # 1. 快照当前预测
    count = snapshot_predictions(theme_id)
    print(f"✅ 快照: {count} 个候选")

    # 2. 评估
    vault_note, note_path = evaluate_predictions(theme_id)
    print(f"📄 报告: {note_path}")
    print()

    # 输出摘要
    print(vault_note[:1500])
    if len(vault_note) > 1500:
        print(f"\n... (完整报告 {len(vault_note)} 字符)")
