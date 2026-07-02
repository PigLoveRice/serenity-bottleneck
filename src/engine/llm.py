# -*- coding: utf-8 -*-
"""LLM API 调用 —— 通过 curl 子进程绕过网络限制。"""

import json
import logging
import subprocess
import sys

from src.config import settings

logger = logging.getLogger(__name__)


def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 3000,
    timeout: int = 300,
) -> str:
    """通过 curl 调用 Hermes LLM API。

    Args:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
        temperature: 温度
        max_tokens: 最大 tokens
        timeout: 超时秒数

    Returns:
        LLM 响应文本
    """
    payload = json.dumps({
        "model": settings.hermes_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    })

    cmd = [
        "curl", "-s",
        "-X", "POST",
        f"{settings.hermes_api_base}/chat/completions",
        "-H", "Content-Type: application/json",
        "-H", f"Authorization: Bearer {settings.hermes_api_key}",
        "-d", payload,
        "--max-time", str(timeout),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 10,
        )

        if result.returncode != 0:
            raise RuntimeError(f"curl 返回非零退出码 {result.returncode}: {result.stderr[:200]}")

        data = json.loads(result.stdout)

        if "error" in data:
            raise RuntimeError(f"API 错误: {data['error']}")

        content = data["choices"][0]["message"]["content"]
        return content

    except subprocess.TimeoutExpired:
        raise RuntimeError(f"LLM API 调用超时 ({timeout}s)")
    except json.JSONDecodeError:
        raise RuntimeError(f"无法解析 LLM 响应: {result.stdout[:300]}")
    except Exception as e:
        raise RuntimeError(f"LLM API 调用失败: {e}")
