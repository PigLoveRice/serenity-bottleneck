# -*- coding: utf-8 -*-
"""飞书推送 —— 群消息 + 云文档双通道。"""

import json
import logging
import os
import time
import requests

from src.config import settings

logger = logging.getLogger(__name__)

DSA_ENV = "/home/daily_stock_analysis/.env"
FEISHU_APP_ID = "cli_aaace90d12fa5cdb"
FEISHU_CHAT_ID = "oc_c0cf7dbd00cbcfdc5a5a03dc7546eacc"
SERENITY_FOLDER_TOKEN = "Bt5Of83trlvPHEdjOZzcQGO1nUh"


def _load_secret() -> str:
    if not os.path.exists(DSA_ENV):
        return ""
    with open(DSA_ENV) as f:
        for line in f:
            if line.startswith("FEISHU_APP_SECRET"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _get_token() -> str:
    secret = _load_secret()
    if not secret:
        return ""
    r = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": secret},
        timeout=10,
    )
    return r.json().get("tenant_access_token", "")


def push_chat_message(text: str) -> bool:
    """推送到飞书群消息。"""
    token = _get_token()
    if not token:
        return False

    if len(text) > 20000:
        text = text[:20000] + "\n...(完整报告见云文档)"

    content = json.dumps({"text": text})
    r = requests.post(
        f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"receive_id": FEISHU_CHAT_ID, "msg_type": "text", "content": content},
        timeout=10,
    )
    return r.json().get("code") == 0


def push_doc(title: str, markdown_text: str) -> str:
    """创建飞书云文档并写入内容。返回 doc_id。"""
    token = _get_token()
    if not token:
        return ""

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 创建文档
    r = requests.post(
        "https://open.feishu.cn/open-apis/docx/v1/documents",
        headers=headers,
        json={"title": title, "folder_token": SERENITY_FOLDER_TOKEN},
        timeout=10,
    )
    result = r.json()
    if result.get("code") != 0:
        logger.error(f"创建文档失败: {result}")
        return ""

    doc_id = result["data"]["document"]["document_id"]
    logger.info(f"飞书文档已创建: {doc_id}")

    # 转换 Markdown → 飞书文本块
    blocks = _md_to_blocks(markdown_text)

    # 分批写入
    total = 0
    for i in range(0, len(blocks), 50):
        batch = blocks[i:i + 50]
        r = requests.post(
            f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
            headers=headers,
            json={"children": batch, "index": -1},
            timeout=15,
        )
        if r.json().get("code") == 0:
            total += len(batch)
        time.sleep(0.3)

    logger.info(f"飞书文档写入 {total} 块")
    return doc_id


def push_full(report_text: str, title: str) -> dict:
    """双通道推送：群消息摘要 + 云文档全文。

    Returns:
        {"chat": bool, "doc_id": str}
    """
    # 1. 群消息：截取前 80 行作为摘要
    lines = report_text.split("\n")
    summary = "\n".join(lines[:80])
    chat_ok = push_chat_message(summary)

    # 2. 云文档：完整内容
    doc_id = push_doc(title, report_text)

    return {"chat": chat_ok, "doc_id": doc_id}


def push_report_file(report_path: str) -> bool:
    """推送报告文件。"""
    from pathlib import Path
    p = Path(report_path)
    if not p.exists():
        return False

    content = p.read_text(encoding="utf-8")
    title = p.stem
    result = push_full(content, title)
    return bool(result["doc_id"])


def _md_to_blocks(text: str) -> list:
    """Markdown 文本转飞书文档块。"""
    lines = text.split("\n")
    blocks = []
    in_table = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            in_table = False
            continue

        # 表格行
        if stripped.startswith("|"):
            clean = stripped.strip("|").replace("**", "")
            blocks.append({
                "block_type": 2,
                "text": {"elements": [{"text_run": {"content": clean}}], "style": {}}
            })
            in_table = True
            continue

        in_table = False

        # 标题
        if stripped.startswith("# "):
            blocks.append({"block_type": 3, "heading1": {
                "elements": [{"text_run": {"content": stripped[2:]}}], "style": {}}})
        elif stripped.startswith("## "):
            blocks.append({"block_type": 4, "heading2": {
                "elements": [{"text_run": {"content": stripped[3:]}}], "style": {}}})
        elif stripped.startswith("### "):
            blocks.append({"block_type": 5, "heading3": {
                "elements": [{"text_run": {"content": stripped[4:]}}], "style": {}}})
        elif stripped.startswith("---"):
            blocks.append({"block_type": 22, "divider": {}})
        else:
            # 清理 markdown 符号
            clean = stripped.replace("**", "").replace("`", "")
            blocks.append({"block_type": 2, "text": {
                "elements": [{"text_run": {"content": clean}}], "style": {}}})

    return blocks
