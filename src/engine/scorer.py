# -*- coding: utf-8 -*-
"""评分引擎 —— 对候选公司进行多维评分。

维度：
1. 趋势对齐度 (trend_alignment): 该候选所处赛道是否与确定性产业趋势对齐
2. 瓶颈卡位度 (bottleneck_score): 该候选在瓶颈环节中的不可替代程度
3. 证据等级 (evidence_grade): P0/P1/P2，影响置信度
4. 估值错配度 (valuation_gap): 当前估值是否反映了产业地位
5. 拥挤度 (sentiment_crowd): 越低越好，说明还没被市场充分定价
"""

import json
import logging

from src.engine.llm import call_llm
from src.engine.json_util import parse_llm_json
from src.methodology.themes import BottleneckTheme
from src.types import SupplyChainLayer, Candidate

logger = logging.getLogger(__name__)

SCORING_PROMPT = """你是一个 A 股产业链投研分析师。对给定的候选公司列表进行五维评分。

输出格式：严格的 JSON 数组，保持输入顺序：
[{
  "stock_name": "公司名",
  "trend_alignment": 0-100,
  "bottleneck_score": 0-100,
  "evidence_grade": "P0/P1/P2",
  "valuation_gap": 0-100,
  "sentiment_crowd": 0-100,
  "evidence_summary": "一两句话说明评分依据的关键证据",
  "risk_flags": ["风险1", "风险2"],
  "coverage_gaps": ["信息缺口1"]
}]

评分标准：
- trend_alignment: 该赛道与 AI/算力/先进制造等确定性趋势的对齐程度。90+ = 已确认的超级周期受益者
- bottleneck_score: 该候选在瓶颈环节中的不可替代性。90+ = 全球仅1-2家供应商，断供行业停摆
- evidence_grade: P0=公告/年报中有直接证据；P1=券商研报交叉验证；P2=仅新闻/逻辑推断
- valuation_gap: 当前估值与产业地位的错配程度。数值高=被低估，数值低=被高估
- sentiment_crowd: 越低越好，代表市场关注度低、机构覆盖少。高分意味着拥挤交易风险

规则：
- 基于你对这些公司的已有知识进行评分，不要编造不存在的数据
- 如果对某公司不了解，相应维度的分适当降低，在 coverage_gaps 中说明
- 每个维度的评分必须有区分度，不要全部给 60-70 的中间分
"""


def score_candidates(
    theme: BottleneckTheme,
    bottlenecks: list[SupplyChainLayer],
    candidates: list[Candidate],
) -> list[Candidate]:
    """对候选列表进行评分。"""
    if not candidates:
        return []

    # 构建瓶颈描述
    bottleneck_desc = "\n".join(
        f"- {bl.name}: {bl.bottleneck_reason} (第{bl.level}层)"
        for bl in bottlenecks
    )

    candidates_desc = "\n".join(
        f"{i+1}. {c.stock_code} {c.stock_name} — {c.bottleneck_role}"
        for i, c in enumerate(candidates)
    )

    user = f"""主题：{theme.label}

瓶颈环节：
{bottleneck_desc}

候选公司：
{candidates_desc}

请对以上候选公司进行五维评分。"""

    output = call_llm(SCORING_PROMPT, user, temperature=0.2, max_tokens=3000)

    scores = parse_llm_json(output, label="评分")

    # 按公司名匹配
    score_map = {}
    for s in scores:
        score_map[s.get("stock_name", "")] = s

    for c in candidates:
        s = score_map.get(c.stock_name, {})
        c.trend_alignment = float(s.get("trend_alignment", 50))
        c.bottleneck_score = float(s.get("bottleneck_score", 50))
        c.evidence_grade = s.get("evidence_grade", "P2")
        c.valuation_gap = float(s.get("valuation_gap", 50))
        c.sentiment_crowd = float(s.get("sentiment_crowd", 50))
        c.evidence_summary = s.get("evidence_summary", "")
        c.risk_flags = s.get("risk_flags", [])
        c.coverage_gaps = s.get("coverage_gaps", [])

        # 加权综合分：瓶颈卡位权重最高，拥挤度是反向指标
        c.total_score = (
            0.15 * c.trend_alignment +
            0.40 * c.bottleneck_score +
            0.15 * c.valuation_gap +
            0.15 * (100 - c.sentiment_crowd) +  # 拥挤度越低分越高
            0.15 * (90 if c.evidence_grade == "P0" else 70 if c.evidence_grade == "P1" else 40)
        )
        c.total_score = round(c.total_score, 1)

    # 按总分降序排列
    candidates.sort(key=lambda c: c.total_score, reverse=True)

    logger.info(f"评分完成: {len(candidates)} 个候选, "
                f"最高分 {candidates[0].total_score if candidates else 'N/A'}")

    return candidates
