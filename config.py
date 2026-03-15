#!/usr/bin/env python3
"""
RTC 实时互动洞察追踪系统 - 共享配置模块

集中管理：赛道关键词、市场关键词、过滤规则、Prompt模板、JSON Schema
"""

import os
import json

# ============================================================
# 基础配置
# ============================================================

WEWE_RSS_BASE_URL = os.getenv("WEWE_RSS_BASE_URL", "http://localhost:4000")
AUTH_CODE = os.getenv("WEWE_RSS_AUTH_CODE", "wewe-rss-2026")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
DATA_DIR = os.getenv("DATA_DIR", "./data")

# 子目录
ARTICLES_DIR = os.path.join(DATA_DIR, "articles")
PROMPTS_DIR = os.path.join(DATA_DIR, "prompts")
ANALYSIS_DIR = os.path.join(DATA_DIR, "analysis")

# 日期过滤起点
DATE_FILTER_START = "2026-01-01"

# Prompt 每篇文章截取字数（全文太长时取摘要）
ARTICLE_EXCERPT_LENGTH = 800

# 单批次最大文章数（超过分批生成 Prompt）
PROMPT_BATCH_SIZE = 25


# ============================================================
# 赛道分类体系（以实时互动为核心视角）
# ============================================================
# 设计原则：
# - 前 4 个赛道是 RTC 核心赛道（高亮显示）
# - 后面是参考赛道，关注它们对 RTC 的间接影响
# - 关键词尽量精确，避免误匹配

TRACK_KEYWORDS = {
    "RTC 音视频": [
        "RTC", "WebRTC", "音视频", "视频通话", "语音通话", "直播连麦",
        "实时音视频", "低延迟", "TRTC", "Agora", "声网", "Pion",
        "视频匹配", "1v1", "视频聊天", "音频技术",
        "推拉流", "编解码", "视频编码", "音频编码", "SFU", "MCU",
        "RTMP", "SRT", "WHIP", "WHEP", "媒体服务器",
    ],
    "IM 即时通讯": [
        "IM", "即时通讯", "消息系统", "群聊", "私信",
        "消息推送", "在线客服", "客服系统", "信令",
        "WhatsApp", "Telegram", "Discord", "聊天系统",
        "环信", "融云", "网易云信",
    ],
    "互动娱乐": [
        "语聊房", "直播PK", "虚拟社交", "秀场直播", "语聊",
        "秀场", "交友", "约会", "Dating", "Social",
        "1v1视频", "视频匹配", "语音社交", "泛娱乐",
        "连麦", "K歌", "在线K歌", "语音房",
        "Bumble", "Tinder", "Hinge", "Azar", "Bigo",
    ],
    "AI + 实时互动": [
        "AI陪聊", "AI陪伴", "AI伴侣", "AI角色", "AI社交",
        "实时翻译", "AI翻译", "AI主播", "AI语音",
        "AI对话", "虚拟人", "数字人", "AI NPC",
        "Character.ai", "AI实时", "语音克隆",
        "AI生成语音", "TTS", "ASR", "语音识别",
        "AI换脸", "实时美颜", "AI美颜", "Replika",
    ],
    "社交泛娱乐": [
        "社交", "社区", "短视频", "直播",
        "Reels", "Shorts", "TikTok", "Instagram",
    ],
    "电商/跨境": [
        "电商", "跨境", "独立站", "Shopify", "TikTok Shop", "Shopee",
        "Lazada", "Temu", "SHEIN", "速卖通", "AliExpress", "亚马逊",
        "Amazon", "直播带货", "DTC", "品牌出海",
    ],
    "游戏": [
        "游戏", "手游", "Game", "Gaming", "SLG", "RPG", "休闲游戏",
        "小游戏", "Roblox", "元宇宙",
    ],
    "短剧 & 内容": [
        "短剧", "ReelShort", "FlexTV", "DramaBox", "微短剧",
        "竖屏剧", "Short Drama", "网文", "小说", "漫画",
        "Webnovel", "有声书",
    ],
    "AI 工具 & 效率": [
        "AI工具", "ChatGPT", "大模型", "LLM", "AIGC", "AI生成",
        "AI助手", "Copilot", "AI Agent", "Claude", "Gemini",
    ],
    "其他出海赛道": [
        "VPN", "支付", "金融", "FinTech", "教育", "EdTech",
        "健康", "运动", "工具出海",
    ],
}

# 赛道优先级（数字越小越靠前）
TRACK_PRIORITY = {
    "RTC 音视频": 0,
    "IM 即时通讯": 1,
    "互动娱乐": 2,
    "AI + 实时互动": 3,
    "社交泛娱乐": 4,
    "AI 工具 & 效率": 5,
    "游戏": 6,
    "电商/跨境": 7,
    "短剧 & 内容": 8,
    "其他出海赛道": 9,
}

# 赛道颜色（用于报告中的标签和图表）
TRACK_COLORS = {
    "RTC 音视频": "#00cec9",
    "IM 即时通讯": "#0984e3",
    "互动娱乐": "#6c5ce7",
    "AI + 实时互动": "#e17055",
    "社交泛娱乐": "#a29bfe",
    "AI 工具 & 效率": "#8b5cf6",
    "游戏": "#00b894",
    "电商/跨境": "#fdcb6e",
    "短剧 & 内容": "#fd79a8",
    "其他出海赛道": "#636e72",
}

# 赛道图标
TRACK_ICONS = {
    "RTC 音视频": "📡",
    "IM 即时通讯": "💬",
    "互动娱乐": "🎭",
    "AI + 实时互动": "🤖",
    "社交泛娱乐": "🎉",
    "AI 工具 & 效率": "⚡",
    "游戏": "🎮",
    "电商/跨境": "🛒",
    "短剧 & 内容": "🎬",
    "其他出海赛道": "📌",
}

# RTC 核心赛道集合（报告中高亮展示）
RTC_TRACKS = {"RTC 音视频", "IM 即时通讯", "互动娱乐", "AI + 实时互动"}


# ============================================================
# 市场/地区关键词
# ============================================================

MARKET_KEYWORDS = {
    "东南亚": ["东南亚", "印尼", "泰国", "越南", "菲律宾", "马来西亚", "新加坡", "SEA", "Indonesia", "Thailand", "Vietnam"],
    "中东": ["中东", "沙特", "阿联酋", "土耳其", "埃及", "MENA", "Saudi", "UAE", "Gulf"],
    "南亚": ["印度", "巴基斯坦", "孟加拉", "南亚", "India", "Pakistan"],
    "拉美": ["拉美", "巴西", "墨西哥", "拉丁美洲", "LATAM", "Brazil", "Mexico", "Argentina"],
    "非洲": ["非洲", "尼日利亚", "肯尼亚", "南非", "Africa", "Nigeria"],
    "北美": ["北美", "美国", "加拿大", "美区", "US Market", "North America"],
    "欧洲": ["欧洲", "英国", "德国", "法国", "Europe", "UK"],
    "日韩": ["日本", "韩国", "日韩", "Japan", "Korea"],
    "全球": ["全球", "Global", "海外", "出海"],
}


# ============================================================
# 文章过滤规则（命中标题关键词的文章不抓取）
# ============================================================

FILTER_KEYWORDS = [
    "招聘", "活动预告", "峰会报名", "线下活动", "直播预约",
    "课程推荐", "广告投放", "合作咨询", "问卷调查",
]


# ============================================================
# AI 分析 Prompt 模板（核心价值点）
# ============================================================

ANALYSIS_PROMPT_TEMPLATE = """# 角色

你是腾讯实时互动(TRTC)产品团队的首席行业分析师。你拥有 10 年 RTC/IM 行业经验，深刻理解音视频技术栈、社交泛娱乐产品形态、以及 AI 对实时互动的颠覆性影响。

# 任务

分析以下 {article_count} 篇出海公众号文章（周期: {period}），输出结构化的行业洞察 JSON。

# 你的分析框架

## 第一层：直接 RTC 信号
- 哪些文章直接提到了音视频通话、直播连麦、语聊房、IM 消息等实时互动场景？
- 有没有新的 App 正在使用或可能使用 RTC/IM SDK？
- 有没有技术趋势影响 RTC 基础设施（如 AI 编解码、端到端加密、边缘计算）？

## 第二层：间接 RTC 机会
- 看似无关的赛道（电商直播带货、游戏语音、AI 陪伴、在线教育）是否暗含 RTC 需求？
- 某个市场的用户行为变化（如中东年轻人社交习惯、东南亚直播电商爆发）是否意味着 RTC 增量？
- 监管政策变化（数据合规、内容审核）对 RTC 出海有什么影响？

## 第三层：竞争与威胁
- Agora(声网)、Livekit、Daily.co 等竞品有什么新动向？
- 大厂（Meta、Google、ByteDance）在实时互动领域有什么布局？
- 开源方案（Pion、Janus、MediaSoup）的进展是否在侵蚀商业 SDK 市场？

# 分析质量要求

1. **洞察要有"So What"** — 不要只说"某 App 融资了"，要分析"这意味着该赛道 RTC 需求将增长，我们应该..."
2. **判断要有立场** — 你是腾讯 RTC 的产品经理，你的判断应该指向"我们该怎么做"
3. **数据要具体** — 引用文章中的具体数据（下载量、收入、融资额、用户数），不要泛泛而谈
4. **趋势要有时间维度** — 这是短期热点还是长期结构性变化？
5. **商机要可执行** — "联系XX团队探讨SDK接入"比"关注该领域"有价值100倍

# 文章内容

{articles}

# 输出格式

请严格输出以下 JSON（不要加任何 markdown 代码块标记）：

{{
    "meta": {{
        "period": "{period}",
        "article_count": {article_count},
        "analyzed_at": "当前时间ISO格式"
    }},
    "tldr": [
        "5-8条本周最重要的事，每条一句话，格式：【赛道标签】具体事件 + 对RTC的启示"
    ],
    "rtc_insights": [
        {{
            "title": "洞察标题（动词开头，如'AI陪伴赛道爆发推动RTC语音需求增长'）",
            "tags": ["相关赛道标签"],
            "body": "300-500字深度分析。要求：1) 现象是什么（引用文章数据） 2) 为什么会这样（底层逻辑） 3) 对RTC意味着什么（产品机会/技术挑战） 4) 预判下一步走势",
            "judgment": "一句话核心判断，要有立场和方向性",
            "opportunity": "对腾讯RTC的具体机会点（要具体到产品动作）",
            "risk": "风险信号或竞争威胁（要具体到竞品名字和动作）",
            "related_articles": ["引用的文章标题"]
        }}
    ],
    "trend_signals": [
        {{
            "signal": "趋势信号（一句话描述）",
            "direction": "rising / falling / emerging",
            "strength": "strong / moderate / weak",
            "evidence": "具体证据，引用文章中的数据点"
        }}
    ],
    "app_discoveries": [
        {{
            "name": "App名称",
            "track": "所属赛道",
            "description": "一句话描述这个App做什么",
            "rtc_relevance": "它用了/可能用了什么实时互动能力（视频通话/语音房/IM消息/直播推流等）",
            "market": "目标市场",
            "data_points": "文章提到的数据（下载量/收入/排名/融资等）"
        }}
    ],
    "business_opportunities": [
        {{
            "title": "商机标题",
            "description": "商机描述（要说清楚为什么是机会、市场有多大）",
            "target_market": "目标市场",
            "urgency": "high / medium / low",
            "action_items": ["具体行动1（如：联系XX团队，了解其音视频方案选型）", "具体行动2"]
        }}
    ],
    "article_classifications": [
        {{
            "title": "原文标题",
            "tracks": ["赛道1", "赛道2"],
            "markets": ["市场1"],
            "apps_mentioned": ["App1"],
            "rtc_relevance": "high / medium / low / none",
            "summary": "一句话概括，突出与RTC的关联"
        }}
    ]
}}

# 质量检查清单

输出前请确认：
- [ ] rtc_insights 至少 3 条，每条 body 超过 300 字
- [ ] 每条 insight 都有明确的"对腾讯RTC意味着什么"
- [ ] trend_signals 至少 5 条，每条都有具体 evidence
- [ ] app_discoveries 中标注了每个 App 的 rtc_relevance
- [ ] business_opportunities 的 action_items 是具体可执行的动作
- [ ] 所有 article 都在 article_classifications 中出现
"""


# ============================================================
# AI 分析 JSON Schema（用于结构校验）
# ============================================================

ANALYSIS_SCHEMA = {
    "type": "object",
    "required": ["meta", "tldr", "rtc_insights", "trend_signals", "app_discoveries", "business_opportunities"],
    "properties": {
        "meta": {
            "type": "object",
            "required": ["period", "article_count", "analyzed_at"],
        },
        "tldr": {"type": "array", "items": {"type": "string"}, "minItems": 3},
        "rtc_insights": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "tags", "body", "judgment"],
            },
            "minItems": 3,
        },
        "trend_signals": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["signal", "direction", "strength"],
            },
            "minItems": 3,
        },
        "app_discoveries": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "track", "description"],
            },
        },
        "business_opportunities": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "description", "urgency"],
            },
        },
    },
}


# ============================================================
# 工具函数
# ============================================================

def validate_analysis(data):
    """
    简单校验分析结果 JSON 是否符合基本结构要求。
    返回 (is_valid, errors) 元组。
    """
    errors = []

    for key in ANALYSIS_SCHEMA["required"]:
        if key not in data:
            errors.append(f"缺少必需字段: {key}")

    if "tldr" in data and len(data["tldr"]) < 3:
        errors.append(f"tldr 至少需要 3 条，当前 {len(data['tldr'])} 条")

    if "rtc_insights" in data:
        if len(data["rtc_insights"]) < 3:
            errors.append(f"rtc_insights 至少需要 3 条，当前 {len(data['rtc_insights'])} 条")
        for i, insight in enumerate(data["rtc_insights"]):
            for field in ["title", "tags", "body", "judgment"]:
                if field not in insight:
                    errors.append(f"rtc_insights[{i}] 缺少字段: {field}")
            if "body" in insight and len(insight["body"]) < 100:
                errors.append(f"rtc_insights[{i}] body 太短（{len(insight['body'])}字），建议 300+ 字")

    if "trend_signals" in data:
        if len(data["trend_signals"]) < 3:
            errors.append(f"trend_signals 至少需要 3 条，当前 {len(data['trend_signals'])} 条")
        for i, sig in enumerate(data["trend_signals"]):
            if "direction" in sig and sig["direction"] not in ("rising", "falling", "emerging"):
                errors.append(f"trend_signals[{i}] direction 无效: {sig['direction']}")

    if "business_opportunities" in data:
        for i, opp in enumerate(data["business_opportunities"]):
            if "urgency" in opp and opp["urgency"] not in ("high", "medium", "low"):
                errors.append(f"business_opportunities[{i}] urgency 无效: {opp['urgency']}")

    return (len(errors) == 0, errors)


def get_track_priority(track_name):
    """获取赛道优先级，未知赛道返回 99"""
    return TRACK_PRIORITY.get(track_name, 99)


def is_rtc_track(track_name):
    """判断是否为 RTC 核心赛道"""
    return track_name in RTC_TRACKS
