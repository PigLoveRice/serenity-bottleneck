# -*- coding: utf-8 -*-
"""飞书文档推送 —— 将筛选报告推送到飞书群。"""

import json
import logging
import os
import requests

from src.config import settings

logger = logging.getLogger(__name__)

# 共享 DSA 的飞书配置
DSA_ENV = "/home/daily_stock_analysis/.env"

FEISHU_CHAT_ID = "oc_c0cf7dbd00cbcfdc5a5a03dc7546eacc"


def _load_feishu_secret() -> str:
    """从 DSA .env 加载飞书密钥。"""
    if not os.path.exists(DSA_ENV):
        return ""
    with open(DSA_ENV) as f:
        for line in f:
            if line.startswith("FEISHU_APP_SECRET"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _get_tenant_token() -> str:
    """获取飞书 tenant_access_token。"""
    secret = _load_feishu_secret()
    if not secret or not settings.feishu_app_id:
        return ""

    r = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": settings.feishu_app_id, "app_secret": secret},
        timeout=10,
    )
    return r.json().get("tenant_access_token", "")


def push_to_feishu(report_text: str, title: str = "") -> bool:
    """推送报告到飞书群。"""
    token = _get_tenant_token()
    if not token:
        logger.warning("飞书 token 获取失败")
        return False

    # 截取摘要作为群消息
    lines = report_text.split("\n")
    # 取前 80 行，足够展示供应链和 TOP 候选
    summary = "\n".join(lines[:80])
    if len(summary) > 20000:
        summary = summary[:20000] + "\n...(完整报告见 runs/ 目录)"

    content = json.dumps({"text": summary})

    r = requests.post(
        f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"receive_id": FEISHU_CHAT_ID, "msg_type": "text", "content": content},
        timeout=10,
    )

    result = r.json()
    if result.get("code") == 0:
        logger.info("✅ 飞书推送成功")
        return True
    else:
        logger.error(f"飞书推送失败: {result.get('msg', result)}")
        return False


def push_report_file(report_path: str) -> bool:
    """推送报告文件到飞书群。"""
    from pathlib import Path
    p = Path(report_path)
    if not p.exists():
        logger.error(f"报告文件不存在: {report_path}")
        return False

    content = p.read_text(encoding="utf-8")
    title = p.stem
    return push_to_feishu(content, title)
