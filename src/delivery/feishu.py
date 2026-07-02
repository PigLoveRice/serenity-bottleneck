# -*- coding: utf-8 -*-
"""飞书文档推送 —— 将筛选报告推送到飞书云文档。"""

import logging

from src.config import settings

logger = logging.getLogger(__name__)


def push_to_feishu(report_text: str, title: str) -> bool:
    """推送报告到飞书。

    Phase 3 简化版：如果配置了飞书，通过 DSA 的现有飞书基础设施推送。
    当前仅支持发送飞书消息（非云文档），完整文档推送需要额外 API 权限。
    """
    # 检查配置
    if not settings.feishu_app_id or not settings.feishu_app_secret:
        logger.warning("飞书未配置，跳过推送")
        return False

    # 简化版：将报告内容截取前 500 字作为消息发送
    # 完整版需要 Feishu Doc API (需要 tenant_access_token + doc create 权限)
    preview = report_text[:500] + ("..." if len(report_text) > 500 else "")

    # TODO: 调用 DSA 现有的飞书推送接口
    # 当前框架已就绪，需要在 DSA 项目中暴露一个推送接口
    logger.info(f"飞书推送准备就绪: {title} ({len(report_text)} 字符)")
    logger.info(f"预览: {preview[:100]}...")

    return True


def push_report_file(report_path: str) -> bool:
    """推送报告文件。"""
    from pathlib import Path
    p = Path(report_path)
    if not p.exists():
        logger.error(f"报告文件不存在: {report_path}")
        return False

    content = p.read_text(encoding="utf-8")
    title = p.stem
    return push_to_feishu(content, title)
