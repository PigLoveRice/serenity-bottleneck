# -*- coding: utf-8 -*-
"""五大瓶颈主题定义 —— 基于 Serenity Bottleneck Theory。"""

from src.types import BottleneckTheme

THEMES: list[BottleneckTheme] = [
    BottleneckTheme(
        id="ai-optical-cpo",
        label="AI 光互联 / CPO / 硅光",
        keywords=[
            "CPO", "光通信", "光模块", "硅光", "光芯片",
            "激光器", "磷化铟", "InP", "光器件", "光电共封装",
            "800G", "1.6T", "MPO", "连接器", "光纤",
            "DFB", "EML", "VCSEL", "外延片", "衬底",
        ],
        positive_signals=[
            "下游 AI capex 扩散", "客户验证通过",
            "产能放量", "国产替代突破",
            "1.6T 量产", "CPO 交换机商用",
        ],
        negative_signals=[
            "铜互连延寿", "客户自研光模块",
            "价格战加剧", "产能扩张过快供需失衡",
            "替代技术路线（LPO 等）",
        ],
    ),
    BottleneckTheme(
        id="power-semi-800vdc",
        label="数据中心电力 / 800VDC / 功率半导体",
        keywords=[
            "功率半导体", "SiC", "碳化硅", "氮化镓", "GaN",
            "800V", "高压直流", "电源管理", "变流器", "逆变器",
            "UPS", "储能", "数据中心电力", "AI 机房",
            "配电", "变压器", "开关电源", "IGBT", "MOSFET",
        ],
        positive_signals=[
            "AI 机柜功率密度提升", "高压直流架构落地",
            "SiC 良率提升", "数据中心配电招标",
        ],
        negative_signals=[
            "传统供电方案延续", "海外龙头降价",
            "SiC 扩产过快", "库存周期下行",
        ],
    ),
    BottleneckTheme(
        id="robotics-supply-chain",
        label="机器人 / 具身智能硬件供应链",
        keywords=[
            "机器人", "减速器", "谐波减速器", "RV 减速器",
            "丝杠", "行星滚柱丝杠", "传感器", "六维力",
            "执行器", "伺服", "稀土", "磁材", "空心杯",
            "电机", "编码器", "轴承", "人形机器人",
            "特斯拉", "Optimus", "具身智能",
        ],
        positive_signals=[
            "量产节点明确", "客户定点",
            "核心零部件瓶颈", "特斯拉供应链导入",
        ],
        negative_signals=[
            "整机进度不及预期", "国产供应商过度拥挤",
            "BOM 降本压力", "技术路线切换（如电机类型）",
        ],
    ),
    BottleneckTheme(
        id="advanced-packaging",
        label="先进封装 / 测试 / 设备材料",
        keywords=[
            "先进封装", "Chiplet", "HBM", "封测",
            "测试设备", "玻璃基板", "ABF", "载板",
            "互连", "CoWoS", "TSV", "RDL",
            "临时键合", "划片", "探针卡", "老化测试",
        ],
        positive_signals=[
            "CoWoS/封装产能约束", "设备验证通过",
            "扩产订单", "国产设备导入",
        ],
        negative_signals=[
            "扩产周期过长", "客户集中风险",
            "技术路线切换", "海外设备禁运",
        ],
    ),
    BottleneckTheme(
        id="sovereign-semi",
        label="半导体自主可控 / 关键设备材料",
        keywords=[
            "半导体", "光刻", "刻蚀", "薄膜", "EDA",
            "材料", "靶材", "电子特气", "晶圆",
            "光刻胶", "CMP", "清洗", "离子注入",
            "检测", "量测", "国产替代",
        ],
        positive_signals=[
            "政策背书", "国产替代突破",
            "供应安全溢价", "大基金三期落地",
        ],
        negative_signals=[
            "估值拥挤", "制裁扰动",
            "验证周期慢", "良率不达预期",
        ],
    ),
]


def get_theme(theme_id: str) -> BottleneckTheme | None:
    for t in THEMES:
        if t.id == theme_id:
            return t
    return None


def list_themes() -> list[str]:
    return [t.id for t in THEMES]
