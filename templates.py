#!/usr/bin/env python3
"""
RTC 实时互动洞察追踪系统 - HTML 模板模块

提供暗色主题 CSS、可复用 HTML 组件、报告模板
"""

from config import TRACK_COLORS, TRACK_ICONS, TRACK_PRIORITY, RTC_TRACKS

# ============================================================
# CSS 变量 & 基础样式
# ============================================================

CSS_VARIABLES = """
:root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #232733;
    --border: #2d3245;
    --text: #e4e6f0;
    --text2: #9299b8;
    --accent: #6c5ce7;
    --accent2: #a29bfe;
    --green: #00b894;
    --orange: #fdcb6e;
    --red: #e17055;
    --blue: #74b9ff;
    --pink: #fd79a8;
    --cyan: #00cec9;
    --rtc-glow: #00cec940;
}
"""

BASE_CSS = CSS_VARIABLES + """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
    line-height: 1.7;
    padding: 0;
}
a { color: var(--accent2); text-decoration: none; }
a:hover { color: var(--blue); }
.container { max-width: 1000px; margin: 0 auto; padding: 30px 20px; }

/* Header — 大渐变背景 */
.page-header {
    text-align: center;
    padding: 60px 20px 40px;
    background: linear-gradient(135deg, #1a1d27 0%, #2d1b69 50%, #1a1d27 100%);
    border-bottom: 1px solid var(--border);
}
.page-header h1 {
    font-size: 2.4em;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent2), var(--cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}
.page-header .subtitle {
    color: var(--text2);
    font-size: 1.05em;
    margin-bottom: 20px;
}
.page-header .meta {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
}
.page-header .meta-item {
    background: rgba(108,92,231,0.15);
    border: 1px solid rgba(108,92,231,0.3);
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 0.85em;
    color: var(--accent2);
}
.page-header .period {
    display: inline-block;
    background: rgba(108,92,231,0.15);
    border: 1px solid rgba(108,92,231,0.3);
    border-radius: 20px;
    padding: 6px 18px;
    margin-top: 14px;
    font-size: 0.9em;
    color: var(--cyan);
}

/* Section */
.section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px;
    margin-bottom: 24px;
}
.section-title {
    font-size: 1.25em;
    font-weight: 700;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--accent);
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-title .icon { font-size: 24px; }

/* Stats Row */
.stats-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 10px;
    margin-bottom: 28px;
}
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
    text-align: center;
}
.stat-card .number {
    font-size: 1.5em;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent2), var(--blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-card .label {
    color: var(--text2);
    font-size: 0.8em;
    margin-top: 3px;
}
.stat-card.rtc-highlight {
    border-color: var(--cyan);
    box-shadow: 0 0 12px var(--rtc-glow);
}
.stat-card.rtc-highlight .number {
    background: linear-gradient(135deg, var(--cyan), #00b894);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* RTC Badge */
.rtc-badge {
    display: inline-block;
    background: linear-gradient(135deg, var(--cyan), var(--accent));
    color: white;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 10px;
    margin-left: 6px;
    vertical-align: middle;
}

/* Tags */
.tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.73em;
    font-weight: 500;
    margin: 2px 4px 2px 0;
}
.tag-rtc {
    background: var(--cyan);
    color: #0f1117;
    font-weight: 600;
}

/* Tables */
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88em;
}
.data-table th {
    background: var(--surface2);
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    color: var(--text2);
    border-bottom: 2px solid var(--border);
    font-size: 0.78em;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.data-table td {
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
}
.data-table tr:hover { background: rgba(108,92,231,0.06); }

/* TL;DR Box */
.tldr-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.tldr-title {
    font-size: 1.15em;
    font-weight: 700;
    color: var(--orange);
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.tldr-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 14px;
    font-size: 0.92em;
    line-height: 1.7;
    color: var(--text);
}
.tldr-item .arrow {
    color: var(--accent2);
    font-size: 1.1em;
    flex-shrink: 0;
    margin-top: 2px;
}
.tldr-item strong { color: var(--orange); }

/* TLDR List (simple) */
.tldr-list { list-style: none; padding: 0; }
.tldr-list li {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 0;
    font-size: 0.92em;
    line-height: 1.7;
    border-bottom: 1px solid var(--border);
}
.tldr-list li:last-child { border-bottom: none; }
.tldr-list li::before {
    content: "→";
    color: var(--accent2);
    font-size: 1.1em;
    flex-shrink: 0;
    margin-top: 1px;
}

/* Insight Card */
.insight-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    transition: border-color 0.2s;
}
.insight-card:hover { border-color: var(--accent); }
.insight-card.rtc-related {
    border-left: 3px solid var(--cyan);
    box-shadow: 0 0 8px var(--rtc-glow);
}
.insight-card h3 {
    font-size: 1.05em;
    font-weight: 700;
    margin-bottom: 8px;
    color: var(--text);
}
.insight-card .body {
    font-size: 0.9em;
    color: var(--text2);
    line-height: 1.8;
    margin: 10px 0;
}
.insight-card .meta-row {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 14px;
}
.insight-card .meta-item {
    font-size: 0.83em;
    padding: 6px 14px;
    border-radius: 8px;
    background: var(--surface);
    border: 1px solid var(--border);
    line-height: 1.5;
}
.insight-card .meta-item.opportunity {
    border-color: var(--green);
    color: var(--green);
}
.insight-card .meta-item.risk {
    border-color: var(--red);
    color: var(--red);
}
.insight-card .meta-item.judgment {
    border-color: var(--orange);
    color: var(--orange);
}

/* Trend Signal */
.trend-signal {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 16px;
    background: var(--surface2);
    border-radius: 10px;
    margin-bottom: 8px;
    font-size: 0.9em;
    line-height: 1.7;
}
.trend-signal .direction {
    display: inline-block;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    text-align: center;
    line-height: 26px;
    font-size: 13px;
    flex-shrink: 0;
}
.trend-signal .direction.rising { background: #00b89420; color: var(--green); }
.trend-signal .direction.falling { background: #e1705520; color: var(--red); }
.trend-signal .direction.emerging { background: #fdcb6e20; color: var(--orange); }
.trend-signal .evidence { font-size: 0.85em; color: var(--text2); margin-top: 4px; }

/* App Discovery Card */
.app-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    transition: border-color 0.2s;
    position: relative;
}
.app-card:hover { border-color: var(--accent); }
.app-card .app-name {
    font-size: 0.95em;
    font-weight: 600;
    color: var(--accent2);
}
.app-card .app-desc { font-size: 0.85em; color: var(--text2); margin: 6px 0; line-height: 1.6; }
.app-card .app-meta { font-size: 0.8em; color: var(--text2); line-height: 1.6; }
.app-card.rtc-app {
    border-color: var(--cyan);
    box-shadow: 0 0 6px var(--rtc-glow);
}
.app-card .new-badge {
    position: absolute;
    top: -6px;
    right: -6px;
    background: linear-gradient(135deg, #e17055, #fd79a8);
    color: white;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 8px;
    letter-spacing: 0.5px;
    box-shadow: 0 2px 6px rgba(225,112,85,0.4);
}
.app-card .rtc-score {
    display: inline-block;
    font-size: 10px;
    font-weight: 600;
    padding: 1px 6px;
    border-radius: 6px;
    margin-left: 6px;
    vertical-align: middle;
}
.app-card .rtc-score.score-high { background: var(--cyan); color: #0f1117; }
.app-card .rtc-score.score-medium { background: rgba(0,206,201,0.3); color: var(--cyan); }
.app-card .rtc-score.score-low { background: rgba(0,206,201,0.1); color: var(--text2); }

/* Business Opportunity */
.biz-opp {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--orange);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 12px;
}
.biz-opp.high { border-left-color: var(--red); }
.biz-opp.medium { border-left-color: var(--orange); }
.biz-opp.low { border-left-color: var(--blue); }
.biz-opp h4 { font-size: 0.95em; font-weight: 700; margin-bottom: 6px; }
.biz-opp .desc { font-size: 0.88em; color: var(--text2); margin: 6px 0; line-height: 1.7; }
.biz-opp .actions { margin-top: 10px; }
.biz-opp .action-item {
    font-size: 0.83em;
    color: var(--text2);
    padding: 4px 0;
    padding-left: 18px;
    position: relative;
    line-height: 1.6;
}
.biz-opp .action-item::before {
    content: "→";
    position: absolute;
    left: 0;
    color: var(--accent2);
}

/* Article List */
.article-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 8px;
    transition: border-color 0.2s;
}
.article-item:hover { border-color: var(--accent); }
.article-item .title {
    font-size: 0.93em;
    font-weight: 600;
    color: var(--text);
}
.article-item .title a { color: var(--text); text-decoration: none; }
.article-item .title a:hover { color: var(--accent2); }
.article-item .meta {
    display: flex;
    gap: 10px;
    margin-top: 5px;
    font-size: 0.78em;
    color: var(--text2);
    flex-wrap: wrap;
}
.article-item .summary {
    font-size: 0.85em;
    color: var(--text2);
    margin-top: 6px;
    line-height: 1.6;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Tab Navigation — 底边框指示条风格 */
.tab-nav {
    display: flex;
    gap: 0;
    border-bottom: 2px solid var(--border);
    background: var(--surface);
    position: sticky;
    top: 0;
    z-index: 100;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
.tab-nav::-webkit-scrollbar { height: 3px; }
.tab-nav::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
.tab-btn {
    flex-shrink: 0;
    padding: 14px 22px;
    font-size: 0.9em;
    font-weight: 600;
    color: var(--text2);
    background: transparent;
    border: none;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: all 0.2s;
    white-space: nowrap;
}
.tab-btn:hover { color: var(--text); background: rgba(108,92,231,0.08); }
.tab-btn.active {
    color: var(--accent2);
    border-bottom-color: var(--accent2);
    background: rgba(108,92,231,0.1);
}
.tab-btn.monthly { color: var(--orange); }
.tab-btn.monthly.active {
    color: var(--orange);
    border-bottom-color: var(--orange);
    background: rgba(253,203,110,0.1);
}
.tab-content { display: none; }
.tab-content.active { display: block; }

/* Footer */
.page-footer {
    text-align: center;
    padding: 30px 20px;
    color: var(--text2);
    font-size: 0.82em;
    border-top: 1px solid var(--border);
    margin-top: 30px;
}

/* Bar Chart */
.bar-chart { display: flex; flex-direction: column; gap: 8px; }
.bar-row {
    display: flex;
    align-items: center;
    gap: 10px;
}
.bar-label {
    width: 120px;
    text-align: right;
    font-size: 0.85em;
    color: var(--text2);
    flex-shrink: 0;
}
.bar-track {
    flex: 1;
    background: var(--surface2);
    border-radius: 6px;
    height: 26px;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 6px;
    display: flex;
    align-items: center;
    padding-left: 10px;
    color: white;
    font-size: 0.78em;
    font-weight: 600;
    min-width: 30px;
    transition: width 0.5s ease;
}

/* Responsive */
@media (max-width: 768px) {
    .container { padding: 12px; }
    .page-header { padding: 40px 16px 28px; }
    .page-header h1 { font-size: 1.8em; }
    .section { padding: 18px; }
    .stats-row { grid-template-columns: repeat(2, 1fr); }
    .insight-card .meta-row { flex-direction: column; }
    .bar-label { width: 80px; font-size: 0.78em; }
    .tab-btn { padding: 12px 14px; font-size: 0.82em; }
}
"""

# ============================================================
# HTML 构建工具函数
# ============================================================

def html_escape(text):
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def build_track_tag(track):
    color = TRACK_COLORS.get(track, "#636e72")
    is_rtc = track in RTC_TRACKS
    cls = "tag tag-rtc" if is_rtc else "tag"
    style = f"background:{color}20;color:{color};border:1px solid {color}40;"
    if is_rtc:
        style = f"background:{color};color:#0f1117;"
    return f'<span class="{cls}" style="{style}">{TRACK_ICONS.get(track, "📌")} {html_escape(track)}</span>'


def build_direction_icon(direction):
    icons = {"rising": "↑", "falling": "↓", "emerging": "★"}
    return f'<span class="direction {direction}">{icons.get(direction, "●")}</span>'


def build_urgency_badge(urgency):
    colors = {"high": "var(--red)", "medium": "var(--orange)", "low": "var(--blue)"}
    labels = {"high": "紧急", "medium": "中等", "low": "关注"}
    c = colors.get(urgency, "var(--text2)")
    return f'<span style="color:{c};font-size:11px;font-weight:600;">[{labels.get(urgency, urgency)}]</span>'


def build_stat_card(number, label, is_rtc=False):
    cls = "stat-card rtc-highlight" if is_rtc else "stat-card"
    return f'''<div class="{cls}">
        <div class="number">{number}</div>
        <div class="label">{html_escape(label)}</div>
    </div>'''


def build_bar_chart(data, max_width_pct=100):
    """data: list of (label, count, color)"""
    if not data:
        return ""
    max_val = max(d[1] for d in data) if data else 1
    html = '<div class="bar-chart">'
    for label, count, color in data:
        width = max(int(count / max_val * max_width_pct), 3) if max_val > 0 else 3
        html += f'''<div class="bar-row">
            <span class="bar-label">{html_escape(label)}</span>
            <div class="bar-track"><div class="bar-fill" style="width:{width}%;background:{color};">{count}</div></div>
        </div>'''
    html += '</div>'
    return html


def build_insight_card(insight):
    """构建洞察卡片 HTML"""
    tags = insight.get("tags", [])
    is_rtc = any(t in RTC_TRACKS for t in tags)
    cls = "insight-card rtc-related" if is_rtc else "insight-card"

    tags_html = " ".join(build_track_tag(t) for t in tags)
    rtc_badge = '<span class="rtc-badge">RTC</span>' if is_rtc else ""

    meta_items = []
    if insight.get("judgment"):
        meta_items.append(f'<span class="meta-item judgment">💡 {html_escape(insight["judgment"])}</span>')
    if insight.get("opportunity"):
        meta_items.append(f'<span class="meta-item opportunity">🎯 {html_escape(insight["opportunity"])}</span>')
    if insight.get("risk"):
        meta_items.append(f'<span class="meta-item risk">⚠️ {html_escape(insight["risk"])}</span>')
    meta_html = f'<div class="meta-row">{"".join(meta_items)}</div>' if meta_items else ""

    refs = insight.get("related_articles", [])
    refs_html = ""
    if refs:
        refs_html = '<div style="margin-top:10px;font-size:0.82em;color:var(--text2);">📎 ' + \
                    "、".join(html_escape(r) for r in refs[:3]) + '</div>'

    return f'''<div class="{cls}">
        <h3>{html_escape(insight.get("title", ""))}{rtc_badge}</h3>
        <div>{tags_html}</div>
        <div class="body">{html_escape(insight.get("body", ""))}</div>
        {meta_html}
        {refs_html}
    </div>'''


def build_trend_signal(signal):
    """构建趋势信号 HTML"""
    direction = signal.get("direction", "emerging")
    strength = signal.get("strength", "moderate")
    strength_labels = {"strong": "🔴 强信号", "moderate": "🟡 中等", "weak": "🔵 弱信号"}

    return f'''<div class="trend-signal">
        {build_direction_icon(direction)}
        <div>
            <div><strong>{html_escape(signal.get("signal", ""))}</strong>
            <span style="font-size:0.8em;color:var(--text2);margin-left:8px;">{strength_labels.get(strength, strength)}</span></div>
            <div class="evidence">{html_escape(signal.get("evidence", ""))}</div>
        </div>
    </div>'''


def get_rtc_relevance_score(app):
    """计算 App 的 RTC 相关度分数 (0-100)，用于排序"""
    score = 0
    track = app.get("track", "")

    # 核心赛道加分
    if track in RTC_TRACKS:
        score += 60
        if track == "RTC 音视频":
            score += 20
        elif track == "互动娱乐":
            score += 15
        elif track == "IM 即时通讯":
            score += 15
        elif track == "AI + 实时互动":
            score += 10

    # rtc_relevance 文本分析加分
    rel = (app.get("rtc_relevance") or "").lower()
    if any(kw in rel for kw in ["高度相关", "核心", "直接", "high"]):
        score += 30
    elif any(kw in rel for kw in ["中度", "中等", "medium"]):
        score += 15
    elif any(kw in rel for kw in ["低", "low"]):
        score += 5

    # 有 rtc_relevance 描述本身加分
    if rel:
        score += 5

    return min(score, 100)


def build_app_card(app, is_new=False):
    """构建 App 发现卡片 HTML"""
    track = app.get("track", "")
    is_rtc = track in RTC_TRACKS
    cls = "app-card rtc-app" if is_rtc else "app-card"
    rtc_badge = '<span class="rtc-badge">RTC</span>' if is_rtc else ""
    new_badge = '<span class="new-badge">NEW</span>' if is_new else ""

    # RTC 相关度评分标签
    rtc_score = get_rtc_relevance_score(app)
    score_html = ""
    if rtc_score >= 60:
        score_html = '<span class="rtc-score score-high">RTC 强相关</span>'
    elif rtc_score >= 20:
        score_html = '<span class="rtc-score score-medium">RTC 关联</span>'

    parts = []
    if app.get("rtc_relevance"):
        parts.append(f'<span style="color:var(--cyan);">📡 {html_escape(app["rtc_relevance"])}</span>')
    if app.get("market"):
        parts.append(f'🌍 {html_escape(app["market"])}')
    if app.get("data_points"):
        parts.append(f'📊 {html_escape(app["data_points"])}')

    return f'''<div class="{cls}">
        {new_badge}
        <div class="app-name">{html_escape(app.get("name", ""))}{rtc_badge}{score_html} {build_track_tag(track) if track else ""}</div>
        <div class="app-desc">{html_escape(app.get("description", ""))}</div>
        <div class="app-meta">{"<br>".join(parts)}</div>
    </div>'''


def build_biz_opp(opp):
    """构建商机卡片 HTML"""
    urgency = opp.get("urgency", "medium")
    actions = opp.get("action_items", [])
    actions_html = ""
    if actions:
        actions_html = '<div class="actions">' + \
                       "".join(f'<div class="action-item">{html_escape(a)}</div>' for a in actions) + \
                       '</div>'

    market = opp.get("target_market", "")
    market_html = f' · 🌍 {html_escape(market)}' if market else ""

    return f'''<div class="biz-opp {urgency}">
        <h4>{build_urgency_badge(urgency)} {html_escape(opp.get("title", ""))}{market_html}</h4>
        <div class="desc">{html_escape(opp.get("description", ""))}</div>
        {actions_html}
    </div>'''


# ============================================================
# 页面模板
# ============================================================

def wrap_html_page(title, body_content, extra_css=""):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_escape(title)}</title>
    <style>{BASE_CSS}{extra_css}</style>
</head>
<body>
{body_content}
</body>
</html>"""


PORTAL_JS = """
<script>
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(function(el) { el.classList.remove('active'); });
    document.querySelectorAll('.tab-btn').forEach(function(el) { el.classList.remove('active'); });
    var target = document.getElementById(tabId);
    if (target) target.classList.add('active');
    // Find and activate the button
    document.querySelectorAll('.tab-btn').forEach(function(btn) {
        if (btn.getAttribute('data-tab') === tabId) {
            btn.classList.add('active');
        }
    });
    window.scrollTo({top: 0, behavior: 'smooth'});
}
</script>
"""
