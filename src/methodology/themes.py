# -*- coding: utf-8 -*-
"""11大瓶颈主题定义 —— 基于 Serenity Bottleneck Theory。"""

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
    # ===== 新增主题 =====
    BottleneckTheme(
        id="oil-gas-equip",
        label="油气勘探设备与服务",
        keywords=[
            "压裂设备", "钻探", "深海油气", "页岩气",
            "油服", "测井", "管道", "LNG",
            "海洋工程", "钻井平台", "完井", "固井",
            "压裂车", "螺杆钻具", "射孔", "录井",
        ],
        positive_signals=[
            "油价维持高位", "深海勘探投资增加",
            "国内能源安全战略", "页岩气规模化开发",
        ],
        negative_signals=[
            "油价大跌", "OPEC+ 减产",
            "新能源替代加速", "环保政策收紧",
        ],
    ),
    BottleneckTheme(
        id="fine-chemical",
        label="精细化工与新材料",
        keywords=[
            "电子特气", "光刻胶", "湿电子化学品", "高端膜材料",
            "PI薄膜", "芳纶", "碳纤维", "功能性涂料",
            "催化剂", "分子筛", "吸附剂", "表面活性剂",
            "OLED材料", "半导体化学品", "抛光液", "清洗液",
        ],
        positive_signals=[
            "国产材料通过晶圆厂验证", "日韩出口管制",
            "大客户导入", "新材料标准制定",
        ],
        negative_signals=[
            "国际巨头降价打压", "客户验证周期长",
            "原材料价格波动", "技术路线变更风险",
        ],
    ),
    BottleneckTheme(
        id="new-energy",
        label="新能源装备与材料",
        keywords=[
            "光伏逆变器", "石英砂", "高纯石英", "风电主轴",
            "风电轴承", "储能系统", "磷酸铁锂", "钠离子电池",
            "隔膜", "电解液", "负极材料", "固态电池",
            "钙钛矿", "HJT", "TOPCon", "海上风电",
        ],
        positive_signals=[
            "光伏装机超预期", "海上风电招标放量",
            "储能政策加码", "技术路线突破（钙钛矿/固态）",
        ],
        negative_signals=[
            "产能过剩价格战", "补贴退坡",
            "海外贸易壁垒", "技术路线迭代过快",
        ],
    ),
    BottleneckTheme(
        id="smart-vehicle",
        label="智能电动汽车供应链",
        keywords=[
            "一体化压铸", "线控底盘", "激光雷达", "碳化硅",
            "自动驾驶", "域控制器", "智能座舱", "动力电池",
            "热管理", "空气悬架", "线控制动", "毫米波雷达",
            "车载摄像头", "高速连接器", "车规MCU", "电驱系统",
        ],
        positive_signals=[
            "新能源渗透率持续提升", "L3自动驾驶法规落地",
            "国产芯片车规认证通过", "海外车企采用中国供应链",
        ],
        negative_signals=[
            "价格战压缩利润", "车企自研替代",
            "技术路线不确定（纯视觉 vs 激光雷达）", "产能过剩",
        ],
    ),
    BottleneckTheme(
        id="xinchuang",
        label="信创国产替代",
        keywords=[
            "CPU", "操作系统", "数据库", "中间件",
            "办公软件", "ERP", "信息安全", "国产服务器",
            "鲲鹏", "飞腾", "麒麟", "统信",
            "达梦", "人大金仓", "东方通", "金山办公",
        ],
        positive_signals=[
            "党政信创全面铺开", "行业信创（金融/电信/能源）加速",
            "国产芯片性能突破", "信创采购目录扩容",
        ],
        negative_signals=[
            "预算约束", "过渡期延长",
            "技术差距缩小慢", "用户习惯迁移阻力大",
        ],
    ),
    BottleneckTheme(
        id="electricity-grid",
        label="电力基础设施与智能电网",
        keywords=[
            "特高压", "变压器", "智能电表", "柔性直流",
            "虚拟电厂", "配电网", "电力物联网", "继电保护",
            "GIS组合电器", "开关柜", "电缆", "调度自动化",
            "抽水蓄能", "调峰调频", "电力交易", "微电网",
        ],
        positive_signals=[
            "电网投资持续加大", "新能源并网需求爆发",
            "特高压新线路核准", "电力市场化改革加速",
        ],
        negative_signals=[
            "电网投资周期性波动", "原材料（铜/硅钢）涨价",
            "地方财政约束项目进度", "分布式光伏冲击配电网",
        ],
    ),
    BottleneckTheme(
        id="ai-server-hardware",
        label="AI 服务器硬件",
        keywords=[
            "AI服务器", "GPU服务器", "液冷散热", "冷板",
            "CDU", "冷却液", "HBM", "高多层PCB",
            "高速背板连接器", "铜箔", "CCL覆铜板",
            "服务器电源", "PSU", "电源模块", "功率电感",
            "机柜", "PDU", "精密空调", "浸没式液冷",
        ],
        positive_signals=[
            "AI 算力投资持续增长", "NVIDIA/AMD 新品量产",
            "液冷渗透率加速提升", "服务器电源功率密度提升",
        ],
        negative_signals=[
            "算力投资周期性回落", "风冷方案延续",
            "铜连接替代光互联", "单机柜功率密度增长放缓",
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
