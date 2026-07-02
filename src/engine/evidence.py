# -*- coding: utf-8 -*-
"""证据提取引擎 —— 对候选公司挖掘公开信息，分级 P0/P1/P2。"""

import json
import logging

from src.engine.llm import call_llm
from src.engine.json_util import parse_llm_json
from src.types import Candidate, EvidenceItem

logger = logging.getLogger(__name__)

EVIDENCE_SYSTEM = """你是一个 A 股信息核查员。对给定的候选公司，从已有知识中提取关键证据，按 P0/P1/P2 标准分级。

输出格式：严格 JSON 数组：
[{
  "grade": "P0 / P1 / P2",
  "source_type": "announcement / report / news / filing",
  "title": "证据标题",
  "claim": "该证据说明什么（一句话）",
  "publisher": "来源方（公司公告/券商/媒体名）"
}]

证据等级：
- P0: 年报/招股书/监管公告中的直接证据，可追溯到具体文件
- P1: 券商研报（交叉验证）、行业标准、大厂供应商名单
- P2: 新闻、产业链逻辑推断、社交媒体线索

规则：
- 只输出你确定知道的事实，不确定的不编造
- 如果没有具体证据，返回空数组 []
- 每条证据的 claim 要具体，不能是"公司不错"这种空话
"""


def extract_evidence(candidate: Candidate) -> list[EvidenceItem]:
    """为单个候选提取证据。

    Returns:
        EvidenceItem 列表，按 P0 > P1 > P2 排序。
    """
    user = f"""候选公司：{candidate.stock_name}（{candidate.stock_code}）
瓶颈定位：{candidate.bottleneck_role}

请提取该候选在瓶颈环节中的关键证据。"""

    output = call_llm(EVIDENCE_SYSTEM, user, temperature=0.1, max_tokens=1000)

    items = parse_llm_json(output, label=f"证据提取 [{candidate.stock_name}]")

    evidence = []
    for item in items:
        evidence.append(EvidenceItem(
            grade=item.get("grade", "P2"),
            source_type=item.get("source_type", "news"),
            title=item.get("title", ""),
            claim=item.get("claim", ""),
            publisher=item.get("publisher", ""),
        ))

    # 按 P0 > P1 > P2 排序
    grade_order = {"P0": 0, "P1": 1, "P2": 2}
    evidence.sort(key=lambda e: grade_order.get(e.grade, 2))

    return evidence


def extract_evidence_batch(candidates: list[Candidate]) -> dict[str, list[EvidenceItem]]:
    """批量为候选提取证据。

    Returns:
        {candidate_id: [EvidenceItem, ...]}
    """
    results = {}
    for c in candidates:
        logger.info(f"  提取证据: {c.stock_name}")
        evidence = extract_evidence(c)
        results[c.stock_code] = evidence
        logger.info(f"    → {len(evidence)} 条 ({', '.join(e.grade for e in evidence)})")
    return results
