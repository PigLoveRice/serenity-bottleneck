# Serenity A 股产业链瓶颈投研 Agent

基于 [Serenity (@serenity)](https://x.com/serenity) "Bottleneck Theory" 的 A 股产业链瓶颈挖掘系统。

## 核心理念

不追龙头，从龙头逆推供应链，找到"缺了它全行业停摆"的隐形瓶颈环节，映射 A 股候选公司。

## 快速开始

```bash
# 1. 安装
pip install -r requirements.txt  # httpx, pydantic, pydantic-settings, python-dotenv

# 2. 配置
cp .env.example .env
# 编辑 .env: HERMES_API_KEY, ANSPIRE_API_KEYS

# 3. 运行
python main.py screen --theme ai-optical-cpo
```

## 命令

| 命令 | 功能 |
|------|------|
| `screen --theme <id>` | 完整筛选：产业链拆解 → 候选搜索 → 评分 → 持久化 → Obsidian |
| `candidates` | 列出活跃候选 |
| `candidate <名>` | 查看候选详情 |
| `evidence:extract <名>` | 提取详细证据链 |
| `kill <名> --reason` | 终止候选 |
| `calibrate` | 校准预测快照 |
| `daily` | 全自动日常任务 |
| `list` | 列出瓶颈主题 |

## 瓶颈主题

- AI 光互联 / CPO / 硅光
- 数据中心电力 / 800VDC / 功率半导体
- 机器人 / 具身智能硬件供应链
- 先进封装 / 测试 / 设备材料
- 半导体自主可控 / 关键设备材料

## Obsidian Vault

项目自带 Obsidian vault，位于 `vault/Serenity-A股产业投研/`：

- `01-主题/` — 瓶颈主题笔记
- `02-候选/` — 候选公司档案（YAML frontmatter + 评分）
- `03-证据/` — 证据条目
- `05-校准/` — 校准报告

用 Obsidian 打开此目录即可查看知识图谱。

## 架构

```
main.py → src/engine/ (供应链拆解 → 候选搜索 → 评分)
       → src/knowledge/ (SQLite → Obsidian vault)
       → src/calibration/ (预测校准)
       → src/delivery/ (飞书推送)
```

## 免责声明

本项目是研究工具，输出研究候选和证据追溯，不构成投资建议。
