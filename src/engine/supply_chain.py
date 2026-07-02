# -*- coding: utf-8 -*-
"""LLM 驱动的产业链拆解引擎。"""

import logging

from src.engine.llm import call_llm
from src.engine.json_util import parse_llm_json
from src.methodology.themes import BottleneckTheme
from src.types import SupplyChainLayer

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个产业链分析专家，擅长对科技产业的供应链进行逐层拆解。

你的任务：给定一个产业主题，从终端需求开始，逐层向上游拆解供应链，直到原材料/基础设备级别。
对每一层，判断它是否构成"瓶颈环节"——即扩产难度极大、认证周期极长、全球只有极少供应商能做的环节。

输出格式：严格的 JSON 数组，每个元素为：
{
  "level": 层级编号（从1开始，1是终端产品/整机），
  "name": "这一层的名称",
  "description": "这一层包含什么，有哪些代表性供应商",
  "is_bottleneck": true/false,
  "bottleneck_reason": "如果是瓶颈，说明原因：产能约束/认证壁垒/寡头格局/良率瓶颈/原材料稀缺"
}

规则：
- 至少拆6层，越往上游越细
- 瓶颈环节不超过总层数的1/3
- 只用你已有的产业知识，不要编造不存在的公司
- 用中文输出
- 确保 JSON 格式完全正确：所有字符串用双引号，数组/对象末尾不要多余逗号
"""


def _build_decompose_prompt(theme: BottleneckTheme) -> str:
    return f"""请对以下产业主题进行供应链拆解：

主题：{theme.label}
关键词：{', '.join(theme.keywords)}
正面信号：{', '.join(theme.positive_signals)}
负面信号：{', '.join(theme.negative_signals)}

请从终端产品/整机开始，逐层向上游拆解供应链，标注瓶颈环节。"""


def decompose_theme(theme: BottleneckTheme) -> list[SupplyChainLayer]:
    """对给定的产业主题进行供应链拆解。"""
    user_prompt = _build_decompose_prompt(theme)
    raw = call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.3, max_tokens=3000)

    items = parse_llm_json(raw, label=f"供应链拆解 [{theme.label}]")
    if not items:
        logger.error(f"供应链 LLM 原始输出:\n{raw[:600]}")
        raise ValueError(f"供应链拆解失败：无法解析 LLM 输出")

    layers = []
    for item in items:
        layers.append(SupplyChainLayer(
            level=item.get("level", len(layers) + 1),
            name=item.get("name", ""),
            description=item.get("description", ""),
            is_bottleneck=item.get("is_bottleneck", False),
            bottleneck_reason=item.get("bottleneck_reason", ""),
        ))

    bottlenecks = [l for l in layers if l.is_bottleneck]
    logger.info(
        f"主题 [{theme.label}] 拆解完成：{len(layers)} 层, "
        f"{len(bottlenecks)} 个瓶颈: {[b.name for b in bottlenecks]}"
    )
    return layers
