# -*- coding: utf-8 -*-
"""SQLite 数据库管理 —— 候选、证据、运行记录。"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

from src.config import settings

DB_PATH = Path(settings.data_dir) / "candidates.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS candidates (
    id              TEXT PRIMARY KEY,
    theme_id        TEXT NOT NULL,
    stock_code      TEXT NOT NULL,
    stock_name      TEXT NOT NULL,
    bottleneck_role TEXT DEFAULT '',
    total_score     REAL DEFAULT 0.0,
    trend_alignment     REAL DEFAULT 0.0,
    bottleneck_score    REAL DEFAULT 0.0,
    evidence_grade      TEXT DEFAULT 'P2',
    valuation_gap       REAL DEFAULT 0.0,
    sentiment_crowd     REAL DEFAULT 0.0,
    status          TEXT DEFAULT 'candidate',
    confidence      TEXT DEFAULT 'low',
    evidence_summary TEXT DEFAULT '',
    risk_flags      TEXT DEFAULT '[]',
    coverage_gaps   TEXT DEFAULT '[]',
    first_seen_at   TEXT DEFAULT '',
    last_seen_at    TEXT DEFAULT '',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    killed_at       TEXT,
    kill_reason     TEXT
);

CREATE TABLE IF NOT EXISTS evidence (
    id              TEXT PRIMARY KEY,
    candidate_id    TEXT NOT NULL REFERENCES candidates(id),
    grade           TEXT NOT NULL,
    source_type     TEXT NOT NULL,
    source_url      TEXT DEFAULT '',
    source_title    TEXT DEFAULT '',
    publisher       TEXT DEFAULT '',
    publish_date    TEXT DEFAULT '',
    claim           TEXT NOT NULL,
    excerpt         TEXT DEFAULT '',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS screen_runs (
    id              TEXT PRIMARY KEY,
    theme_id        TEXT NOT NULL,
    run_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    layers_count    INTEGER DEFAULT 0,
    bottlenecks     TEXT DEFAULT '[]',
    candidates_found INTEGER DEFAULT 0,
    new_candidates  INTEGER DEFAULT 0,
    duration_seconds REAL DEFAULT 0,
    report_path     TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_candidates_theme ON candidates(theme_id);
CREATE INDEX IF NOT EXISTS idx_candidates_score ON candidates(total_score DESC);
CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status);
CREATE INDEX IF NOT EXISTS idx_evidence_candidate ON evidence(candidate_id);
CREATE INDEX IF NOT EXISTS idx_evidence_grade ON evidence(grade);
CREATE INDEX IF NOT EXISTS idx_runs_theme ON screen_runs(theme_id);

CREATE TABLE IF NOT EXISTS calibration (
    id              TEXT PRIMARY KEY,
    candidate_id    TEXT NOT NULL REFERENCES candidates(id),
    prediction_date TEXT NOT NULL,
    target_date     TEXT NOT NULL,
    predicted_score REAL DEFAULT 0,
    actual_outcome  TEXT,
    actual_return   REAL,
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cal_candidate ON calibration(candidate_id);
CREATE INDEX IF NOT EXISTS idx_cal_date ON calibration(prediction_date);
"""


def get_db() -> sqlite3.Connection:
    """获取数据库连接（自动建表）。"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    return conn


def upsert_candidate(conn: sqlite3.Connection, candidate) -> str:
    """插入或更新候选记录。按 stock_code + theme_id 去重。
    
    Returns:
        candidate_id
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 查找已有候选
    existing = conn.execute(
        "SELECT id, first_seen_at, status FROM candidates WHERE stock_code=? AND theme_id=?",
        (candidate.stock_code, candidate.theme_id)
    ).fetchone()
    
    risk_json = json.dumps(candidate.risk_flags, ensure_ascii=False)
    gaps_json = json.dumps(candidate.coverage_gaps, ensure_ascii=False)
    
    if existing:
        cid = existing["id"]
        first_seen = existing["first_seen_at"]
        # 不覆盖 killed 的候选
        if existing["status"] == "killed":
            return cid
        
        conn.execute("""
            UPDATE candidates SET
                total_score=?, trend_alignment=?, bottleneck_score=?,
                evidence_grade=?, valuation_gap=?, sentiment_crowd=?,
                evidence_summary=?, risk_flags=?, coverage_gaps=?,
                last_seen_at=?, updated_at=?
            WHERE id=?
        """, (
            candidate.total_score, candidate.trend_alignment, candidate.bottleneck_score,
            candidate.evidence_grade, candidate.valuation_gap, candidate.sentiment_crowd,
            candidate.evidence_summary, risk_json, gaps_json,
            now, now, cid
        ))
        return cid
    else:
        import uuid
        cid = uuid.uuid4().hex[:12]
        conn.execute("""
            INSERT INTO candidates (id, theme_id, stock_code, stock_name, bottleneck_role,
                total_score, trend_alignment, bottleneck_score, evidence_grade,
                valuation_gap, sentiment_crowd, evidence_summary, risk_flags, coverage_gaps,
                first_seen_at, last_seen_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            cid, candidate.theme_id, candidate.stock_code, candidate.stock_name,
            candidate.bottleneck_role, candidate.total_score, candidate.trend_alignment,
            candidate.bottleneck_score, candidate.evidence_grade,
            candidate.valuation_gap, candidate.sentiment_crowd,
            candidate.evidence_summary, risk_json, gaps_json,
            now, now
        ))
        return cid


def insert_evidence(conn: sqlite3.Connection, candidate_id: str, evidence) -> str:
    """插入证据记录。去重（相同 url + claim）。"""
    import uuid
    
    existing = conn.execute(
        "SELECT id FROM evidence WHERE candidate_id=? AND source_url=? AND claim=?",
        (candidate_id, evidence.url, evidence.claim)
    ).fetchone()
    
    if existing:
        return existing["id"]
    
    eid = uuid.uuid4().hex[:10]
    conn.execute("""
        INSERT INTO evidence (id, candidate_id, grade, source_type, source_url,
            source_title, publisher, publish_date, claim, excerpt)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        eid, candidate_id, evidence.grade, evidence.source_type,
        evidence.url, evidence.title, evidence.publisher,
        evidence.date, evidence.claim, evidence.excerpt
    ))
    return eid


def record_run(conn: sqlite3.Connection, run_id: str, theme_id: str,
               layers_count: int, bottlenecks: list, candidates_count: int,
               new_count: int, duration: float, report_path: str):
    """记录一次筛选运行。"""
    conn.execute("""
        INSERT INTO screen_runs (id, theme_id, layers_count, bottlenecks,
            candidates_found, new_candidates, duration_seconds, report_path)
        VALUES (?,?,?,?,?,?,?,?)
    """, (
        run_id, theme_id, layers_count,
        json.dumps(bottlenecks, ensure_ascii=False),
        candidates_count, new_count, round(duration, 1), report_path
    ))


def list_candidates(conn: sqlite3.Connection, theme_id: str = None,
                     status: str = None, limit: int = 50) -> list:
    """列出候选。"""
    where = []
    params = []
    if theme_id:
        where.append("theme_id=?")
        params.append(theme_id)
    if status:
        where.append("status=?")
        params.append(status)
    
    sql = "SELECT * FROM candidates"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY total_score DESC LIMIT ?"
    params.append(limit)
    
    return conn.execute(sql, params).fetchall()


def get_candidate(conn: sqlite3.Connection, stock_name: str) -> dict | None:
    """按名称查找候选。"""
    row = conn.execute(
        "SELECT * FROM candidates WHERE stock_name LIKE ? LIMIT 1",
        (f"%{stock_name}%",)
    ).fetchone()
    return dict(row) if row else None


def get_evidence(conn: sqlite3.Connection, candidate_id: str) -> list:
    """获取候选的证据链。"""
    return conn.execute(
        "SELECT * FROM evidence WHERE candidate_id=? ORDER BY grade, created_at DESC",
        (candidate_id,)
    ).fetchall()


def kill_candidate(conn: sqlite3.Connection, stock_name: str, reason: str):
    """标记候选为已终止。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute(
        "UPDATE candidates SET status='killed', killed_at=?, kill_reason=? WHERE stock_name LIKE ?",
        (now, reason, f"%{stock_name}%")
    )
