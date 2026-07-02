# -*- coding: utf-8 -*-
"""数据模型定义。"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class BottleneckTheme:
    id: str
    label: str
    keywords: list[str]
    positive_signals: list[str]
    negative_signals: list[str]


@dataclass
class SupplyChainLayer:
    level: int
    name: str
    description: str
    is_bottleneck: bool = False
    bottleneck_reason: str = ""


@dataclass
class Candidate:
    theme_id: str
    stock_code: str          # 600519.SH
    stock_name: str
    bottleneck_role: str      # 瓶颈定位描述
    total_score: float = 0.0
    # 分项
    trend_alignment: float = 0.0
    bottleneck_score: float = 0.0
    evidence_grade: str = "P2"
    valuation_gap: float = 0.0
    sentiment_crowd: float = 0.0
    # 元数据
    status: str = "candidate"
    confidence: str = "low"
    evidence_summary: str = ""
    risk_flags: list[str] = field(default_factory=list)
    coverage_gaps: list[str] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M")


@dataclass
class ScreenResult:
    run_id: str
    theme: BottleneckTheme
    supply_chain: list[SupplyChainLayer]
    candidates: list[Candidate]
    summary: str = ""
    run_at: str = ""

    def __post_init__(self):
        if not self.run_at:
            self.run_at = datetime.now().strftime("%Y-%m-%d %H:%M")


@dataclass
class EvidenceItem:
    grade: str              # P0 / P1 / P2
    source_type: str        # announcement / news / report / filing
    title: str
    claim: str
    url: str = ""
    publisher: str = ""
    date: str = ""
