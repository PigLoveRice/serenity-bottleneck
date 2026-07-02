# -*- coding: utf-8 -*-
"""A 股候选搜索引擎。

输入：瓶颈主题 + 供应链层级
输出：A 股候选公司列表
"""

import json
import logging
import os
import subprocess

from src.config import settings
from src.engine.llm import call_llm
from src.engine.json_util import parse_llm_json
from src.methodology.themes import BottleneckTheme
from src.types import SupplyChainLayer, Candidate

logger = logging.getLogger(__name__)

ANSPIRE_URL = "https://plugin.anspire.cn/api/ntsearch/search"


def _get_anspire_key() -> str:
    """获取第一个 Anspire API key。"""
    keys = settings.anspire_api_keys or os.getenv("ANSPIRE_API_KEYS", "")
    return keys.split(",")[0].strip()


def _search_anspire(query: str, top_k: int = 10) -> list[dict]:
    """通过 Anspire 搜索 A 股相关信息。"""
    key = _get_anspire_key()
    if not key:
        logger.warning("Anspire API key 未配置，跳过搜索")
        return []

    try:
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        cmd = [
            "curl", "-s",
            f"{ANSPIRE_URL}?query={encoded_query}&top_k={top_k}",
            "-H", f"Authorization: Bearer {key}",
            "--max-time", "30",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        data = json.loads(result.stdout)
        return data.get("results", []) or data.get("data", {}).get("results", [])
    except Exception as e:
        logger.warning(f"Anspire 搜索失败 [{query[:30]}]: {e}")
        return []


def _build_search_queries(theme: BottleneckTheme, bottlenecks: list[SupplyChainLayer]) -> list[str]:
    """构建针对瓶颈环节的 A 股搜索查询。"""
    queries = []

    # 1. 主题级搜索：主题标签 + "A股 概念股 龙头"
    queries.append(f"{theme.label} A股 概念股 龙头 供应商")

    # 2. 瓶颈级搜索：每个瓶颈 + "A股 上市公司"
    for bl in bottlenecks:
        queries.append(f"{bl.name} A股 上市公司 概念股")

    # 3. 关键词组合搜索
    top_keywords = theme.keywords[:5]
    queries.append(f"{' '.join(top_keywords)} A股 股票 列表")

    return queries


def _extract_candidates_from_search(
    theme: BottleneckTheme,
    results: list[dict],
) -> list[Candidate]:
    """从搜索结果中提取候选公司。"""

    # 把所有搜索结果拼接成文本，让 LLM 提取
    text_parts = []
    for r in results[:15]:
        title = r.get("title", "")
        content = r.get("content", "")[:500]
        url = r.get("url", "")
        text_parts.append(f"标题: {title}\n摘要: {content}\n来源: {url}\n")

    if not text_parts:
        return []

    combined = "\n---\n".join(text_parts)

    system = """你是一个 A 股行业研究员。从搜索结果中提取与给定产业主题直接相关的 A 股上市公司。

输出格式：严格的 JSON 数组，每个元素为：
{
  "stock_code": "股票代码，如 300502.SZ（深市）.SH（沪市），如果搜索结果中没有完整代码，用股票名称",
  "stock_name": "股票名称",
  "bottleneck_role": "该公司在产业链瓶颈环节中的定位，一两句话描述它卡什么位置、为什么重要",
  "relevance": "high/medium/low"
}

规则：
- 只提取 A 股上市公司（深交所 .SZ / 上交所 .SH）
- 代码格式必须是 6 位数字 + 市场后缀
- 如果搜索结果中提到某公司但无法确定代码，不要编造，跳过
- 按相关性排序，最多返回 10 个
- 港股（.HK）和美股不要包括在内
"""

    user = f"""主题：{theme.label}
搜索关键词：{', '.join(theme.keywords[:8])}

搜索结果：
{combined}

请提取 A 股候选公司。"""

    output = call_llm(system, user, temperature=0.1, max_tokens=2000)

    items = parse_llm_json(output, label=f"候选提取 [{theme.label}]")

    candidates = []
    for item in items:
        code = item.get("stock_code", "").strip()
        name = item.get("stock_name", "").strip()
        if not name:
            continue

        # 标准化代码格式
        if "." in code:
            pass  # 已有市场后缀
        elif code.isdigit() and len(code) == 6:
            if code.startswith(("6", "9")):
                code = f"{code}.SH"
            elif code.startswith(("0", "2", "3")):
                code = f"{code}.SZ"
            elif code.startswith("4") or code.startswith("8"):
                code = f"{code}.BJ"

        candidates.append(Candidate(
            theme_id=theme.id,
            stock_code=code,
            stock_name=name,
            bottleneck_role=item.get("bottleneck_role", ""),
            total_score=0.0,
            evidence_grade="P2",  # 初始等级，后续评分阶段调整
        ))

    return candidates


def screen_candidates(
    theme: BottleneckTheme,
    bottlenecks: list[SupplyChainLayer],
) -> list[Candidate]:
    """主入口：对主题进行 A 股候选筛选。"""
    queries = _build_search_queries(theme, bottlenecks)
    logger.info(f"搜索 {len(queries)} 个查询: {[q[:40] for q in queries]}")

    all_results = []
    for q in queries:
        results = _search_anspire(q, top_k=10)
        all_results.extend(results)
        logger.info(f"  查询 [{q[:40]}...] → {len(results)} 条结果")

    # 去重
    seen_urls = set()
    unique_results = []
    for r in all_results:
        url = r.get("url", "")
        if url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(r)

    logger.info(f"去重后 {len(unique_results)} 条结果")

    candidates = _extract_candidates_from_search(theme, unique_results)

    # 去重（按股票代码）
    seen_codes = set()
    unique_candidates = []
    for c in candidates:
        key = c.stock_code or c.stock_name
        if key not in seen_codes:
            seen_codes.add(key)
            unique_candidates.append(c)

    logger.info(f"提取 {len(unique_candidates)} 个候选: {[c.stock_name for c in unique_candidates]}")

    return unique_candidates
