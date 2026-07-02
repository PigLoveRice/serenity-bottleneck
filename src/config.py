# -*- coding: utf-8 -*-
"""配置管理 —— 从环境变量加载。"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Hermes LLM
    hermes_api_base: str = "http://127.0.0.1:8642/v1"
    hermes_model: str = "deepseek-v4-pro"
    hermes_api_key: str = "not-needed"

    # Anspire
    anspire_api_keys: str = ""

    # FinanceMCP
    financemcp_url: str = "https://finvestai.top/mcp"
    financemcp_token: str = ""

    # 飞书
    feishu_app_id: str = ""
    feishu_app_secret: str = ""

    # 路径
    vault_root: str = "vault/Serenity-A股产业投研"
    runs_dir: str = "runs"
    data_dir: str = "data"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
