# -*- coding: utf-8 -*-
"""JSON 解析工具 —— LLM 输出容错解析。"""

import json
import logging
import re

logger = logging.getLogger(__name__)


def parse_llm_json(raw: str, label: str = "JSON") -> list:
    """多策略解析 LLM 输出的 JSON 数组。

    处理常见问题：markdown 代码块包裹、尾部逗号、
    换行符、编码问题等。

    Returns:
        解析后的 list，解析失败返回 []。
    """
    raw = raw.strip()

    # 1. 去除 markdown 代码块
    if raw.startswith("```"):
        lines = raw.split("\n")
        # 跳过 ```json / ``` 标记行
        start_idx = 1 if lines[0].strip() in ("```", "```json") else 0
        raw = "\n".join(lines[start_idx:])
    if raw.endswith("```"):
        raw = raw[:-3].strip()

    # 2. 提取 [...] 部分
    start = raw.find("[")
    end = raw.rfind("]")
    if start < 0 or end < start:
        logger.warning(f"{label}: 未找到 JSON 数组 [{start}:{end}]")
        return []

    segment = raw[start:end + 1]

    # 3. 修复常见 JSON 错误
    # 尾部逗号
    segment = re.sub(r',\s*]', ']', segment)
    segment = re.sub(r',\s*}', '}', segment)
    # 单引号
    # (暂不处理，LLM 通常输出双引号)

    # 4. 解析
    try:
        return json.loads(segment)
    except json.JSONDecodeError as e:
        logger.warning(f"{label} 解析失败: {e}")
        logger.warning(f"原始片段 (前300字符): {segment[:300]}")
        return []
