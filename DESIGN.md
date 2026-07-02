# Serenity 产业链瓶颈投研 Agent — DESIGN.md

> 基于 Serenity "Bottleneck Theory" 的 A 股产业链瓶颈挖掘系统。
> Python 实现，独立于 DSA 项目，窄而深地覆盖 5 大瓶颈主题。

---

## 1. 项目定位

**与 DSA 的本质区别：**

| 维度 | DSA | Serenity Agent |
|------|-----|----------------|
| 起点 | 个股代码 | 产业主题 |
| 路径 | 代码 → 数据 → 分析 → 报告 | 主题 → 供应链拆解 → 瓶颈定位 → 候选筛选 → 证据验证 |
| 核心问题 | "这只股票该买/卖吗？" | "AI 集群扩 10 倍后什么会先不够用？哪个 A 股公司卡在这个环节？" |
| 数据依赖 | 行情 + 技术指标 + 财务 + 新闻 | 产业链知识 + 公告/财报/新闻交叉验证 |
| 输出 | 个股分析报告 | 瓶颈候选清单 + 证据链 + 置信度评分 |

**定位：** 不做交易决策，只产出研究候选和证据追溯。不提供买卖建议。

---

## 2. 核心方法论

```
产业趋势（确定性的）
    ↓
产业链全景拆解（LLM 辅助）
    ↓
瓶颈环节定位（卡产能/卡材料/卡良率/卡认证）
    ↓
A 股映射（谁卡在这个环节？）
    ↓
多维交叉验证（公告 + 财报 + 新闻 + 客户映射）
    ↓
候选评分 + 证据等级 → 输出
```

## 2.1 五大瓶颈主题（Phase 1）

| ID | 主题 | 核心瓶颈方向 |
|----|------|-------------|
| ai-optical-cpo | AI 光互联 / CPO / 硅光 | InP 衬底、DFB 激光器、硅光 foundry、MPO 连接器 |
| power-semi-800vdc | 数据中心电力 / 800VDC / 功率半导体 | SiC 衬底、GaN 器件、高压直流电源 |
| robotics-supply-chain | 机器人 / 具身智能硬件供应链 | 谐波减速器、行星滚柱丝杠、六维力传感器、空心杯电机 |
| advanced-packaging | 先进封装 / 测试 / 设备材料 | CoWoS 封装材料、HBM 测试设备、玻璃基板 |
| sovereign-semi | 半导体自主可控 / 关键设备材料 | 光刻胶、电子特气、靶材、EDA |

---

## 3. 技术架构

```
┌─────────────────────────────────────────────────┐
│                   CLI / Cron                      │
│          main.py screen / review / calibrate     │
├─────────────────────────────────────────────────┤
│                                                 │
│   ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│   │  Theme   │  │ Supply   │  │  Screener    │  │
│   │ Registry │→ │ Chain    │→ │  (A-share    │  │
│   │ (5主题)  │  │ Mapper   │  │   mapping)   │  │
│   └──────────┘  └──────────┘  └──────┬──────┘  │
│                                      │          │
│   ┌──────────────────────────────────┘          │
│   ▼                                              │
│   ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│   │ Evidence │  │ Scoring  │  │ Calibration  │  │
│   │ Pipeline │→ │ Rubric   │→ │ Tracker      │  │
│   └────┬─────┘  └──────────┘  └─────────────┘  │
│        │                                         │
├────────┼─────────────────────────────────────────┤
│        ▼           Data Layer                     │
│   ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│   │ SQLite   │  │ Obsidian │  │ FinanceMCP   │  │
│   │(候选/证据)│  │  Vault   │  │ + Anspire    │  │
│   └──────────┘  └──────────┘  └─────────────┘  │
├─────────────────────────────────────────────────┤
│                    Delivery                       │
│   ┌──────────┐  ┌──────────┐                     │
│   │ Markdown │  │  Feishu  │                     │
│   │  Report  │  │  Doc/msg │                     │
│   └──────────┘  └──────────┘                     │
└─────────────────────────────────────────────────┘
```

## 3.1 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 语言 | Python 3.12 | 复用 Hermes/FinanceMCP/飞书等现有基础设施 |
| LLM | Hermes API (DeepSeek V4 Pro) | 供应链拆解、候选评估、报告生成 |
| 搜索 | Anspire API + FinanceMCP | 新闻/公告/财报检索 |
| 数据库 | SQLite (WAL 模式) | 候选记录、证据条目、校准数据 |
| 知识库 | Obsidian Vault (Markdown) | 主题笔记、候选档案、研报存根、证据链 |
| 调度 | cron (systemd timer) | 每日自动筛选 |
| 交付 | Markdown 文件 + 飞书文档 | 报告输出 |

## 3.2 为什么用 Obsidian

- Obsidian vault 本质就是 Markdown 文件目录，Python 直接读写
- 不需要 Obsidian 客户端运行，服务器上纯文件操作
- 天然支持双向链接（`[[候选/xxx]]`）、标签、图谱
- 你可以选装 Obsidian 客户端远程查看 vault（SFTP 挂载或 Git 同步）
- 与原 serenity-a-share-trading-agent 的知识管理方式一致

---

## 4. 目录结构

```
/home/serenity-bottleneck/
├── DESIGN.md
├── README.md
├── .env                        # ANSPIRE_API_KEYS, HERMES_API_BASE, etc.
├── pyproject.toml
├── main.py                     # CLI 入口
│
├── src/
│   ├── config.py               # 配置管理 (pydantic-settings)
│   ├── types.py                # 数据模型 (Candidate, Evidence, Theme...)
│   │
│   ├── methodology/
│   │   ├── themes.py           # 五大瓶颈主题定义
│   │   ├── rubric.py           # 评分矩阵 (趋势对齐/瓶颈定位/证据/估值)
│   │   └── methodology.md      # 完整方法论文本（注入 LLM prompt）
│   │
│   ├── engine/
│   │   ├── supply_chain.py     # LLM 驱动的产业链拆解
│   │   ├── screener.py         # A 股候选筛选
│   │   ├── evidence.py         # 证据提取与分级 (P0/P1/P2)
│   │   └── scorer.py           # 综合评分引擎
│   │
│   ├── knowledge/
│   │   ├── obsidian.py         # Obsidian vault 读写
│   │   └── source_registry.py  # 信息来源注册与追踪
│   │
│   ├── calibration/
│   │   ├── tracker.py          # 预测记录
│   │   └── evaluator.py        # Brier Score / Log Loss / ECE
│   │
│   └── delivery/
│       ├── report.py           # Markdown 报告生成
│       └── feishu.py           # 飞书文档推送
│
├── vault/                      # Obsidian vault 根目录
│   └── Serenity-A股产业投研/
│       ├── 00-方法论.md
│       ├── 01-主题/
│       │   ├── AI光互联CPO硅光.md
│       │   ├── 数据中心电力800VDC.md
│       │   ├── 机器人具身智能供应链.md
│       │   ├── 先进封装测试设备材料.md
│       │   └── 半导体自主可控.md
│       ├── 02-候选/
│       │   └── (每个候选公司一个 .md)
│       ├── 03-证据/
│       │   └── (按来源 P0/P1/P2 组织)
│       ├── 04-信号/
│       │   └── (从新闻/公告中提取的关键信号)
│       ├── 05-校准/
│       │   └── (预测记录与回顾)
│       └── 99-模板/
│           ├── 候选模板.md
│           └── 证据模板.md
│
├── runs/                       # 运行产物（不入库）
│   ├── screen_YYYYMMDD_HHMM.md
│   └── calibration_YYYYMMDD.json
│
└── data/
    ├── candidates.db           # SQLite 数据库
    └── source_registry.json    # 信息来源注册表
```

---

## 5. 数据库设计

### 5.1 candidates 表

```sql
CREATE TABLE candidates (
    id              TEXT PRIMARY KEY,          -- UUID
    theme_id        TEXT NOT NULL,             -- 瓶颈主题 ID
    stock_code      TEXT NOT NULL,             -- 股票代码 (600519.SH)
    stock_name      TEXT NOT NULL,
    bottleneck_role TEXT NOT NULL,             -- 瓶颈定位描述
    total_score     REAL DEFAULT 0.0,          -- 综合评分 (0-100)
    -- 分项评分
    trend_alignment     REAL DEFAULT 0.0,      -- 趋势对齐度
    bottleneck_score    REAL DEFAULT 0.0,      -- 瓶颈卡位度
    evidence_grade      TEXT DEFAULT 'P2',     -- 最高证据等级 P0/P1/P2
    valuation_gap       REAL DEFAULT 0.0,      -- 估值错配度
    sentiment_crowd     REAL DEFAULT 0.0,      -- 情绪/拥挤度 (越低越好)
    -- 状态
    status          TEXT DEFAULT 'candidate',  -- candidate/watching/graduated/killed
    confidence      TEXT DEFAULT 'low',        -- low/medium/high
    evidence_summary TEXT,                     -- 证据摘要
    risk_flags      TEXT,                      -- 风险标记 (JSON array)
    coverage_gaps   TEXT,                      -- 覆盖缺口 (JSON array)
    source_ids      TEXT,                      -- 来源 ID 列表 (JSON array)
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    graduated_at    TIMESTAMP,
    killed_at       TIMESTAMP,
    kill_reason     TEXT
);

CREATE INDEX idx_candidates_theme ON candidates(theme_id);
CREATE INDEX idx_candidates_score ON candidates(total_score DESC);
CREATE INDEX idx_candidates_status ON candidates(status);
```

### 5.2 evidence 表

```sql
CREATE TABLE evidence (
    id              TEXT PRIMARY KEY,
    candidate_id    TEXT NOT NULL REFERENCES candidates(id),
    grade           TEXT NOT NULL,             -- P0/P1/P2
    source_type     TEXT NOT NULL,             -- announcement/report/news/filing
    source_url      TEXT,
    source_title    TEXT,
    publisher       TEXT,                      -- 发布方
    publish_date    TEXT,
    claim           TEXT NOT NULL,             -- 核心主张
    excerpt         TEXT,                      -- 原文摘录
    obsidian_note   TEXT,                      -- Obsidian 笔记路径
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_evidence_candidate ON evidence(candidate_id);
CREATE INDEX idx_evidence_grade ON evidence(grade);
```

### 5.3 calibration 表

```sql
CREATE TABLE calibration (
    id              TEXT PRIMARY KEY,
    candidate_id    TEXT NOT NULL REFERENCES candidates(id),
    prediction_date TEXT NOT NULL,             -- 预测日期
    target_date     TEXT NOT NULL,             -- 目标日期
    predicted_score REAL,                      -- 预测评分
    actual_outcome  TEXT,                      -- realized/missed/partial
    actual_return   REAL,                      -- 实际涨跌幅 (%)
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.4 screen_runs 表

```sql
CREATE TABLE screen_runs (
    id              TEXT PRIMARY KEY,
    run_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    themes_screened TEXT,                      -- JSON array of theme IDs
    candidates_found INTEGER DEFAULT 0,
    new_candidates  INTEGER DEFAULT 0,
    duration_seconds REAL,
    error_log       TEXT
);
```

---

## 6. CLI 命令

```bash
# 核心命令
python main.py screen                          # 全主题筛选，输出候选报告
python main.py screen --theme ai-optical-cpo   # 单主题筛选
python main.py screen --theme ai-optical-cpo --depth deep  # 深度模式（更多证据检索）

# 候选管理
python main.py candidates                      # 列出所有候选
python main.py candidates --theme ai-optical-cpo  # 按主题过滤
python main.py candidate <id>                  # 查看候选详情
python main.py kill <id> --reason "..."        # 标记候选为失败

# 证据管理
python main.py evidence <candidate_id>         # 查看证据链
python main.py evidence:refresh <candidate_id> # 刷新证据

# 校准
python main.py calibrate                       # 校准历史预测
python main.py calibration:report              # 生成校准报告

# 知识库
python main.py vault:init                      # 初始化 Obsidian vault
python main.py vault:sync                      # 同步候选到 vault

# 飞书
python main.py feishu:push <run_id>            # 推送报告到飞书

# 调度
python main.py cron                            # 打印 crontab 配置
python main.py daily                           # 每日自动运行 (screen + calibrate)
```

---

## 7. 核心流程

### 7.1 每日筛选流程 (screen)

```
1. 加载五大瓶颈主题
2. 对每个主题：
   a. 注入方法论 + 主题定义 → LLM 拆解产业链层级
   b. LLM 定位瓶颈环节："哪个环节扩产最难/认证最长/寡头最集中？"
   c. 瓶颈关键词 → Anspire + FinanceMCP 搜索 A 股相关公司
   d. 对每个候选公司：
      - 抓取最新公告/财报（FinanceMCP）
      - 搜索相关新闻（Anspire）
      - 评分矩阵计算（趋势对齐 × 瓶颈卡位 × 证据等级 × 估值错配 ÷ 拥挤度）
      - 写入 SQLite + Obsidian vault
   e. 按评分排序，输出 TOP 候选
3. 生成 Markdown 筛选报告
4. 推送飞书（如有配置）
```

### 7.2 证据分级标准

| 等级 | 定义 | 示例来源 |
|------|------|---------|
| **P0** | 直接可追溯的一手证据 | 年报、招股书、监管公告、客户/供应商公开材料 |
| **P1** | 多源归纳的强信号 | 券商研报（交叉验证）、行业标准文件、大厂供应商名单 |
| **P2** | 框架推断或间接信号 | 新闻、产业链逻辑推理、社交媒体线索（仅作线索不可单独采信） |

---

## 8. 分阶段路线图

### Phase 1 — 核心筛选（MVP，1-2 天）

- [x] 项目骨架搭建
- [ ] 五大主题定义 (`src/methodology/themes.py`)
- [ ] 方法论文本 (`src/methodology/methodology.md`)
- [ ] LLM 供应链拆解引擎
- [ ] A 股候选搜索（Anspire + FinanceMCP）
- [ ] 评分矩阵（简化版：只用 LLM 评分，不做多因子加权）
- [ ] Markdown 报告生成
- [ ] CLI 入口 (`main.py screen`)
- [ ] SQLite 数据库初始化

**Phase 1 验证标准：** 运行 `python main.py screen --theme ai-optical-cpo`，输出一份包含候选公司、瓶颈定位、证据摘要、评分的 Markdown 报告。

### Phase 2 — 知识库（2-3 天）

- [ ] Obsidian vault 初始化与同步
- [ ] 候选自动生成 vault 笔记
- [ ] 证据链追踪（P0/P1/P2 分级）
- [ ] 信息来源注册表
- [ ] 研报/公告自动归档到 vault

### Phase 3 — 校准与自动化（1-2 天）

- [ ] 候选评分历史追踪
- [ ] Brier Score / Log Loss 校准
- [ ] 飞书文档推送
- [ ] Cron 每日自动运行
- [ ] 校准报告生成

---

## 9. 与 DSA 的关系

**完全独立项目，不相互依赖。** 唯一共享的是基础设施：

| 共享资源 | 方式 |
|---------|------|
| Hermes API (DeepSeek V4 Pro) | 各自配置 `HERMES_API_BASE` / `DEEPSEEK_API_KEY` |
| FinanceMCP | 各自配置 MCP 端点 |
| Anspire 搜索 | 共用 `ANSPIRE_API_KEYS`（从 `.env` 读取） |
| 飞书 | 可共用 App Bot，或新建独立 Bot |

DSA 继续做个股技术面分析 + 持仓跟踪；Serenity Agent 做产业链瓶颈挖掘 + 候选筛选。两者可以互补：Serenity 发现的候选可以导入 DSA 做深度技术面分析。

---

## 10. 风险与局限

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| LLM 供应链幻觉 | 高 | 每条瓶颈线索必须有可查证的公开信息支撑；无证据标注"框架推断" |
| 公开信息不足以支撑深度瓶颈分析 | 高 | 明确标注覆盖缺口；不做无据断言 |
| 搜索结果噪声（A 股小票信息少） | 中 | 关键词设计覆盖公司全称/简称/行业 |
| 评分主观性 | 中 | Phase 3 用校准数据反向调整权重 |
| 券商研报缺失（vs 原项目 FFD MCP） | 中 | 接受 P1 以下证据的局限性；优先挖掘公告和年报 |

---

## 11. 下一步

确认本设计后，Phase 1 实现顺序：
1. 创建项目骨架 → 2. 主题定义 + 方法论 → 3. 供应链拆解 → 4. A 股映射 → 5. 评分 → 6. CLI 入口
