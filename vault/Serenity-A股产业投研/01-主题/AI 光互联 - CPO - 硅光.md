---
theme_id: "ai-optical-cpo"
updated: "2026-07-02 18:37"
tags: [主题, ai-optical-cpo]
---

# AI 光互联 / CPO / 硅光

## 关键词

CPO, 光通信, 光模块, 硅光, 光芯片, 激光器, 磷化铟, InP

## 上次扫描

2026-07-02 18:37 — 找到 10 个候选

## 瓶颈环节

- **光电核心芯片（DSP / Driver / TIA / 硅光PIC）**（L4）: DSP芯片寡头格局：Marvell与Broadcom两家垄断PAM4 DSP全方案，设计壁垒极高（SerDes+DSP算法复合技术），认证周期18-24个月，任何新进入者需要同时跨越模拟设计、数字设计、信号完整性三道门槛。
- **有源光芯片（EML/DFB激光器、高速探测器）**（L5）: 高速EML激光器芯片良率瓶颈：200G/lane EML芯片良率仅50-60%，全球仅Lumentum、Coherent、Broadcom三家能量产，认证周期超过18个月。激光器芯片是光模块的「心脏」，一旦缺货整个光模块产业链停摆，且扩产涉及外延→晶圆→芯片的多环节协调，扩产周期长达2-3年。
- **衬底材料（InP / GaAs / SOI衬底）**（L7）: InP衬底寡头格局+扩产极难：住友电工全球垄断超60%，单晶生长工艺壁垒极高（VGF炉一次生长需1个月，位错密度控制要求<500/cm²），全球年产能仅~300万片（4英寸等效），且从4英寸向6英寸过渡极慢。新进入者从建产线到客户认证通常需5年以上，一旦AI需求爆发式增长，InP衬底将是最硬的上游约束。

## 候选

```dataview
TABLE total_score, evidence_grade, bottleneck_role
FROM "02-候选"
WHERE theme = "ai-optical-cpo" AND status != "killed"
SORT total_score DESC
```
