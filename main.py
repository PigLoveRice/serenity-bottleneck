# -*- coding: utf-8 -*-
"""Serenity 产业链瓶颈投研 Agent — CLI 入口。"""

import logging
import sys
import time
import uuid

from src.config import settings
from src.methodology.themes import THEMES, get_theme, list_themes
from src.engine.supply_chain import decompose_theme
from src.engine.screener import screen_candidates
from src.engine.scorer import score_candidates
from src.engine.evidence import extract_evidence_batch
from src.delivery.report import generate_report, save_report
from src.knowledge.database import (
    get_db, upsert_candidate, insert_evidence, record_run,
    list_candidates, get_candidate, get_evidence, kill_candidate,
)
from src.knowledge.obsidian import (
    write_candidate_note, write_evidence_note, write_theme_note,
)
from src.calibration.tracker import cmd_calibrate
from src.delivery.feishu import push_full
from src.types import ScreenResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("serenity")


def cmd_screen(theme_id: str):
    """执行一次完整的瓶颈筛选（Phase 1 + Phase 2）。"""
    t0 = time.time()
    theme = get_theme(theme_id)
    if not theme:
        print(f"❌ 未知主题: {theme_id}")
        print(f"可用主题: {list_themes()}")
        sys.exit(1)

    run_id = uuid.uuid4().hex[:8]
    db = get_db()

    print(f"🔍 开始投研: {theme.label} (run={run_id})")
    print()

    # Phase 1: 供应链拆解 + 候选搜索 + 评分
    print("📡 正在拆解产业链...")
    supply_chain = decompose_theme(theme)
    bottlenecks = [l for l in supply_chain if l.is_bottleneck]
    print(f"   拆解完成: {len(supply_chain)} 层, {len(bottlenecks)} 个瓶颈")
    for bl in bottlenecks:
        print(f"   🔴 L{bl.level} {bl.name}")
    print()

    print("🔎 正在搜索 A 股候选...")
    candidates = screen_candidates(theme, bottlenecks)
    print(f"   找到 {len(candidates)} 个候选")
    print()

    if candidates:
        print("📊 正在评分...")
        candidates = score_candidates(theme, bottlenecks, candidates)
        print(f"   TOP 3:")
        for i, c in enumerate(candidates[:3]):
            print(f"   {i+1}. {c.stock_name} ({c.stock_code}) — {c.total_score:.1f}分")
        print()

        # Phase 2: 持久化 + Obsidian
        print("💾 正在持久化到 SQLite...")
        new_count = 0
        for c in candidates:
            cid = upsert_candidate(db, c)
            if cid:
                new_count += 1
        db.commit()
        print(f"   持久化: {new_count} 个候选（含新增和更新）")
        print()

        # Phase 2: Obsidian vault（证据摘要来自评分阶段，不单独提取）
        print("📝 正在写入 Obsidian vault...")
        for c in candidates:
            write_candidate_note(c, theme.label, evidence_items=[])
        write_theme_note(theme.id, theme.label, theme.keywords, bottlenecks, len(candidates))
        print(f"   vault 已更新")
        print()
        print(f"💡 提示: 运行 'python main.py evidence:extract <公司名>' 为单个候选提取详细证据链")
        print()
    else:
        new_count = 0

    # 生成报告
    result = ScreenResult(
        run_id=run_id,
        theme=theme,
        supply_chain=supply_chain,
        candidates=candidates,
    )
    report = generate_report(result)
    path = save_report(report, theme_id)

    # 记录运行
    duration = time.time() - t0
    record_run(db, run_id, theme_id, len(supply_chain),
               [b.name for b in bottlenecks], len(candidates),
               new_count, duration, str(path))
    db.commit()
    db.close()

    print(f"📄 报告: {path}")
    print(f"⏱️  耗时: {duration:.0f}s")

    # Phase 3: 飞书推送（群消息 + 云文档）
    result = push_full(report, f"{theme.label}_{run_id}")
    if result["doc_id"]:
        print(f"📎 飞书文档: https://bytedance.feishu.cn/docx/{result['doc_id']}")

    print()
    print("=" * 60)
    print(report[:1500])
    if len(report) > 1500:
        print(f"\n... (完整报告 {len(report)} 字符)")


def cmd_candidates(theme_id: str = None, status: str = None):
    """列出候选公司。"""
    db = get_db()
    rows = list_candidates(db, theme_id=theme_id, status=status)
    db.close()

    if not rows:
        print("暂无候选。")
        return

    print(f"{'公司':<10} {'代码':<12} {'主题':<25} {'评分':>6} {'证据':>4} {'状态':<10}")
    print("-" * 75)
    for r in rows:
        print(f"{r['stock_name']:<10} {r['stock_code']:<12} "
              f"{r['theme_id']:<25} {r['total_score']:>6.1f} "
              f"{r['evidence_grade']:>4} {r['status']:<10}")


def cmd_candidate_detail(name: str):
    """查看候选详情。"""
    db = get_db()
    c = get_candidate(db, name)
    if not c:
        print(f"❌ 未找到: {name}")
        db.close()
        return

    print(f"\n{'='*50}")
    print(f"{c['stock_name']}（{c['stock_code']}）")
    print(f"主题: {c['theme_id']}  |  评分: {c['total_score']:.1f}  |  状态: {c['status']}")
    print(f"瓶颈定位: {c['bottleneck_role']}")
    print()
    print(f"趋势对齐: {c['trend_alignment']:.0f}  瓶颈卡位: {c['bottleneck_score']:.0f}")
    print(f"证据等级: {c['evidence_grade']}  估值错配: {c['valuation_gap']:.0f}  拥挤度: {c['sentiment_crowd']:.0f}")
    print(f"证据摘要: {c['evidence_summary']}")
    print()

    # 证据链
    ev_rows = get_evidence(db, c['id'])
    if ev_rows:
        print("证据链:")
        for ev in ev_rows:
            print(f"  [{ev['grade']}] {ev['claim']}")
            print(f"       来源: {ev['publisher']} ({ev['source_type']})")
    else:
        print("暂无证据记录。")

    db.close()


def cmd_kill(name: str, reason: str = ""):
    """标记候选为已终止。"""
    db = get_db()
    kill_candidate(db, name, reason)
    db.commit()
    db.close()
    print(f"✅ 已标记 {name} 为 killed")


def cmd_evidence(name: str):
    """查看候选的证据链（同 candidate 但只显示证据部分）。"""
    db = get_db()
    c = get_candidate(db, name)
    if not c:
        print(f"❌ 未找到: {name}")
        db.close()
        return

    ev_rows = get_evidence(db, c['id'])
    db.close()

    if not ev_rows:
        print(f"{name}: 暂无证据记录。")
        return

    print(f"\n{name} 证据链 ({len(ev_rows)} 条):")
    for ev in ev_rows:
        print(f"  [{ev['grade']}] {ev['claim']}")
        print(f"      {ev['publisher']} — {ev['source_title']}")


def cmd_evidence_extract(name: str):
    """为单个候选提取详细证据链。"""
    db = get_db()
    c = get_candidate(db, name)
    if not c:
        print(f"❌ 未找到: {name}")
        db.close()
        return

    from src.types import Candidate, EvidenceItem
    candidate = Candidate(
        theme_id=c["theme_id"],
        stock_code=c["stock_code"],
        stock_name=c["stock_name"],
        bottleneck_role=c["bottleneck_role"],
    )

    print(f"📋 提取证据: {c['stock_name']} ({c['stock_code']})")
    evidence = extract_evidence(candidate)
    print(f"   提取到 {len(evidence)} 条证据")
    
    for ev in evidence:
        insert_evidence(db, c["id"], ev)
        print(f"   [{ev.grade}] {ev.claim[:80]}")
    
    db.commit()
    
    # 更新 Obsidian
    write_candidate_note(candidate, "", evidence)
    for ev in evidence:
        write_evidence_note(ev, candidate.stock_name)
    
    db.close()
    print(f"✅ 已保存到数据库和 Obsidian vault")


def cmd_list():
    """列出所有主题。"""
    print("可用瓶颈主题：")
    for t in THEMES:
        keywords_preview = ", ".join(t.keywords[:5])
        print(f"  {t.id}")
        print(f"    {t.label}")
        print(f"    关键词: {keywords_preview}...")
        print()


def cmd_run_all():
    """对所有主题执行筛选。"""
    for t in THEMES:
        print(f"\n{'='*60}")
        cmd_screen(t.id)


def main():
    if len(sys.argv) < 2:
        print("Serenity 产业链瓶颈投研 Agent")
        print()
        print("用法:")
        print("  python main.py screen [--theme <id>]    产业投研 + 持久化 + Obsidian")
        print("  python main.py candidates [--theme <id>] 列出候选")
        print("  python main.py candidates --killed       列出已终止候选")
        print("  python main.py candidate <name>          查看候选详情")
        print("  python main.py evidence <name>           查看证据链")
        print("  python main.py evidence:extract <name>    为候选提取详细证据（含 Obsidian）")
        print("  python main.py kill <name> [--reason]    标记候选为已终止")
        print("  python main.py calibrate [--theme <id>]  校准历史预测")
        print("  python main.py daily                      每日自动任务 (screen + calibrate)")
        print("  python main.py list                      列出所有瓶颈主题")
        print("  python main.py run-all                   对所有主题执行筛选")
        print()
        print(f"可用主题: {list_themes()}")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "list":
        cmd_list()
    elif cmd == "screen":
        theme_id = "ai-optical-cpo"
        if "--theme" in sys.argv:
            idx = sys.argv.index("--theme")
            if idx + 1 < len(sys.argv):
                theme_id = sys.argv[idx + 1]
        cmd_screen(theme_id)
    elif cmd == "candidates":
        theme_id = None
        status = None
        if "--theme" in sys.argv:
            idx = sys.argv.index("--theme")
            if idx + 1 < len(sys.argv):
                theme_id = sys.argv[idx + 1]
        if "--killed" in sys.argv:
            status = "killed"
        cmd_candidates(theme_id, status)
    elif cmd == "candidate":
        if len(sys.argv) < 3:
            print("用法: python main.py candidate <公司名>")
            sys.exit(1)
        cmd_candidate_detail(sys.argv[2])
    elif cmd == "kill":
        if len(sys.argv) < 3:
            print("用法: python main.py kill <公司名> [--reason ...]")
            sys.exit(1)
        reason = ""
        if "--reason" in sys.argv:
            idx = sys.argv.index("--reason")
            if idx + 1 < len(sys.argv):
                reason = sys.argv[idx + 1]
        cmd_kill(sys.argv[2], reason)
    elif cmd == "evidence":
        if len(sys.argv) < 3:
            print("用法: python main.py evidence <公司名>")
            sys.exit(1)
        cmd_evidence(sys.argv[2])
    elif cmd == "evidence:extract":
        if len(sys.argv) < 3:
            print("用法: python main.py evidence:extract <公司名>")
            sys.exit(1)
        cmd_evidence_extract(sys.argv[2])
    elif cmd == "calibrate":
        theme_id = None
        if "--theme" in sys.argv:
            idx = sys.argv.index("--theme")
            if idx + 1 < len(sys.argv):
                theme_id = sys.argv[idx + 1]
        cmd_calibrate(theme_id)
    elif cmd == "daily":
        print("🔄 每日自动任务")
        for t in THEMES:
            print(f"\n--- {t.label} ---")
            cmd_screen(t.id)
        cmd_calibrate()
    elif cmd == "run-all":
        cmd_run_all()
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
