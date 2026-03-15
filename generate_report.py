#!/usr/bin/env python3
"""
RTC 实时互动洞察追踪系统 - 报告生成脚本

Step 3: 读取 AI 分析结果 JSON → 生成 HTML 周报/月报/门户

用法：
    python3 generate_report.py weekly --period 2026-03-09_2026-03-15
    python3 generate_report.py monthly --month 2026-03
    python3 generate_report.py portal
"""

import json
import os
import sys
import re
import argparse
import glob
from datetime import datetime
from collections import Counter, defaultdict

from config import (
    DATA_DIR, OUTPUT_DIR, ARTICLES_DIR, ANALYSIS_DIR,
    TRACK_COLORS, TRACK_ICONS, TRACK_PRIORITY, RTC_TRACKS,
)
from templates import (
    html_escape, build_track_tag, build_direction_icon,
    build_urgency_badge, build_stat_card, build_bar_chart,
    build_insight_card, build_trend_signal, build_app_card, build_biz_opp,
    wrap_html_page, BASE_CSS, PORTAL_JS, get_rtc_relevance_score,
)


# ============================================================
# 数据加载
# ============================================================

def load_analysis(period_str):
    """加载分析结果 JSON。period_str 格式：2026-03-09_2026-03-15"""
    filepath = os.path.join(ANALYSIS_DIR, f"analysis_{period_str}.json")
    if not os.path.exists(filepath):
        # 尝试目录模糊匹配
        pattern = os.path.join(ANALYSIS_DIR, f"analysis_{period_str}*.json")
        matches = glob.glob(pattern)
        if matches:
            filepath = matches[0]
        else:
            print(f"  [错误] 找不到分析文件: {filepath}")
            print(f"  请先在 CodeBuddy 中让 Claude 分析文章并保存到 {ANALYSIS_DIR}/")
            return None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 检查是否已分析（tldr 不为空）
    if not data.get("tldr"):
        print(f"  [警告] 分析文件存在但内容为空: {filepath}")
        print(f"  请先在 CodeBuddy 中让 Claude 完成分析")
        return None

    return data


def load_articles(period_str):
    """加载文章 JSON"""
    filepath = os.path.join(ARTICLES_DIR, f"articles_{period_str}.json")
    if not os.path.exists(filepath):
        pattern = os.path.join(ARTICLES_DIR, f"articles_{period_str}*.json")
        matches = glob.glob(pattern)
        if matches:
            filepath = matches[0]
        else:
            return None

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_app_tracker():
    """加载 App 追踪数据"""
    tracker_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_tracker.json")
    if os.path.exists(tracker_path):
        with open(tracker_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"apps": {}, "weeks": []}


def save_app_tracker(data):
    tracker_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_tracker.json")
    with open(tracker_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_app_tracker_from_analysis(analysis):
    """根据 AI 分析结果更新 App 追踪"""
    tracker = load_app_tracker()
    period = analysis.get("meta", {}).get("period", "")

    if period and period not in tracker.get("weeks", []):
        tracker.setdefault("weeks", []).append(period)

    for app in analysis.get("app_discoveries", []):
        name = app.get("name", "")
        if not name:
            continue

        if name not in tracker["apps"]:
            tracker["apps"][name] = {
                "name": name,
                "track": app.get("track", "其他"),
                "first_seen_date": datetime.now().strftime("%Y-%m-%d"),
                "first_seen_week": period,
                "description": app.get("description", ""),
                "rtc_relevance": app.get("rtc_relevance", ""),
                "mention_count": 1,
                "weeks_mentioned": [period],
                "sources": [],
                "data_points": app.get("data_points", ""),
            }
        else:
            existing = tracker["apps"][name]
            existing["mention_count"] = existing.get("mention_count", 0) + 1
            if period not in existing.get("weeks_mentioned", []):
                existing.setdefault("weeks_mentioned", []).append(period)
            if app.get("rtc_relevance") and not existing.get("rtc_relevance"):
                existing["rtc_relevance"] = app["rtc_relevance"]

    save_app_tracker(tracker)
    return tracker


# ============================================================
# 周报 HTML 生成
# ============================================================

def generate_weekly_html(analysis, articles_data=None):
    """生成周报 HTML"""
    period = analysis.get("meta", {}).get("period", "未知周期")
    article_count = analysis.get("meta", {}).get("article_count", 0)
    tldr = analysis.get("tldr", [])
    insights = analysis.get("rtc_insights", [])
    trends = analysis.get("trend_signals", [])
    apps = analysis.get("app_discoveries", [])
    opportunities = analysis.get("business_opportunities", [])
    classifications = analysis.get("article_classifications", [])

    # 统计
    rtc_insights_count = len(insights)
    rtc_apps = [a for a in apps if any(t in RTC_TRACKS for t in [a.get("track", "")])]
    biz_high = [o for o in opportunities if o.get("urgency") == "high"]

    # --- Header ---
    header = f'''
    <div class="page-header">
        <h1>📡 RTC 实时互动洞察周报</h1>
        <div class="subtitle">腾讯实时互动 · 出海趋势追踪</div>
        <div class="meta">
            <span class="meta-item">📄 {article_count} 篇文章</span>
            <span class="meta-item">📡 {rtc_insights_count} 条 RTC 洞察</span>
            <span class="meta-item">📱 {len(apps)} 个新 App</span>
            <span class="meta-item">📈 {len(trends)} 条趋势信号</span>
        </div>
        <div class="period">{html_escape(period)}</div>
    </div>
    <div class="container">
    '''

    # --- Stats ---
    stats = '<div class="stats-row">'
    stats += build_stat_card(article_count, "分析文章数")
    stats += build_stat_card(rtc_insights_count, "RTC 洞察", is_rtc=True)
    stats += build_stat_card(len(apps), "新发现 App")
    stats += build_stat_card(len(trends), "趋势信号")
    stats += build_stat_card(len(biz_high), "紧急商机", is_rtc=len(biz_high) > 0)
    stats += '</div>'

    # --- TL;DR ---
    tldr_html = '<div class="tldr-box"><div class="tldr-title">⚡ 本周速览 TL;DR</div>'
    for item in tldr:
        tldr_html += f'<div class="tldr-item"><span class="arrow">→</span><span>{html_escape(item)}</span></div>'
    tldr_html += '</div>'

    # --- App Discoveries (放在 TL;DR 之后) ---
    # 加载 app_tracker 判断哪些是新 App
    tracker = load_app_tracker()
    current_period = analysis.get("meta", {}).get("period", "")

    # 按 RTC 相关度排序
    sorted_apps = sorted(apps, key=lambda a: get_rtc_relevance_score(a), reverse=True)

    apps_html = '<div class="section"><div class="section-title"><span class="icon">📱</span> 客户列表 · App 发现沉淀</div>'
    apps_html += '<p style="font-size:0.85em;color:var(--text2);margin-bottom:16px;">按 RTC 相关度排序 · <span style="color:var(--cyan);">■</span> RTC 强相关 · <span class="new-badge" style="position:static;display:inline-block;background:linear-gradient(135deg,#e17055,#fd79a8);color:white;font-size:10px;font-weight:700;padding:2px 8px;border-radius:8px;">NEW</span> 本周新发现</p>'
    apps_html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;">'
    for app in sorted_apps:
        app_name = app.get("name", "")
        # 判断是否为本周新发现的 App
        is_new = False
        if app_name in tracker.get("apps", {}):
            tracked = tracker["apps"][app_name]
            first_week = tracked.get("first_seen_week", "")
            if first_week == current_period:
                is_new = True
        else:
            is_new = True  # 不在 tracker 中，视为新发现
        apps_html += build_app_card(app, is_new=is_new)
    apps_html += '</div></div>'

    # --- RTC Insights ---
    insights_html = '<div class="section"><div class="section-title"><span class="icon">📡</span> RTC 实时互动洞察</div>'
    for insight in insights:
        insights_html += build_insight_card(insight)
    insights_html += '</div>'

    # --- Trend Signals ---
    trends_html = '<div class="section"><div class="section-title"><span class="icon">📈</span> 趋势信号</div>'
    for direction in ["rising", "emerging", "falling"]:
        dir_trends = [t for t in trends if t.get("direction") == direction]
        if not dir_trends:
            continue
        dir_labels = {"rising": "🟢 升温趋势", "emerging": "🟡 新兴趋势", "falling": "🔴 降温趋势"}
        trends_html += f'<h4 style="font-size:14px;color:var(--text2);margin:16px 0 8px;">{dir_labels.get(direction, direction)}</h4>'
        for t in dir_trends:
            trends_html += build_trend_signal(t)
    trends_html += '</div>'

    # --- Business Opportunities ---
    opp_html = '<div class="section"><div class="section-title"><span class="icon">💰</span> 商机线索</div>'
    for opp in sorted(opportunities, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("urgency", ""), 3)):
        opp_html += build_biz_opp(opp)
    opp_html += '</div>'

    # --- Article Classifications ---
    articles_html = ""
    if classifications:
        # 建立标题→链接映射（从原始文章数据）
        title_to_link = {}
        if articles_data:
            raw_articles = articles_data.get("articles", articles_data) if isinstance(articles_data, dict) else articles_data
            if isinstance(raw_articles, list):
                for art in raw_articles:
                    if isinstance(art, dict) and art.get("title") and art.get("link"):
                        title_to_link[art["title"]] = art["link"]

        # 按 rtc_relevance 排序
        relevance_order = {"high": 0, "medium": 1, "low": 2, "none": 3}
        sorted_cls = sorted(classifications, key=lambda x: relevance_order.get(x.get("rtc_relevance", "none"), 4))

        articles_html = '<div class="section"><div class="section-title"><span class="icon">📰</span> 文章分类总览</div>'
        articles_html += '<table class="data-table"><thead><tr>'
        articles_html += '<th>文章</th><th>赛道</th><th>RTC 关联</th><th>摘要</th>'
        articles_html += '</tr></thead><tbody>'
        for cls in sorted_cls:
            relevance = cls.get("rtc_relevance", "none")
            rel_colors = {"high": "var(--cyan)", "medium": "var(--green)", "low": "var(--text2)", "none": "var(--border)"}
            rel_labels = {"high": "⬤ 高", "medium": "◉ 中", "low": "○ 低", "none": "· 无"}

            tracks_tags = " ".join(build_track_tag(t) for t in cls.get("tracks", []))
            title = cls.get("title", "")
            link = title_to_link.get(title, "")
            if link:
                title_html = f'<a href="{html_escape(link)}" target="_blank" style="color:var(--accent2);text-decoration:none;border-bottom:1px dashed var(--accent2);">{html_escape(title)}</a>'
            else:
                title_html = f'<strong>{html_escape(title)}</strong>'
            articles_html += f'''<tr>
                <td style="max-width:300px;">{title_html}</td>
                <td>{tracks_tags}</td>
                <td style="color:{rel_colors.get(relevance, "var(--text2)")}">{rel_labels.get(relevance, relevance)}</td>
                <td style="font-size:12px;color:var(--text2);">{html_escape(cls.get("summary", ""))}</td>
            </tr>'''
        articles_html += '</tbody></table></div>'

    # --- Footer ---
    footer = f'''
    <div class="page-footer">
        RTC 实时互动洞察追踪系统 · 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")} · Powered by Claude AI
    </div>
    </div>'''

    body = header + stats + tldr_html + apps_html + insights_html + trends_html + opp_html + articles_html + footer
    return wrap_html_page(f"RTC 周报 | {period}", body)


# ============================================================
# 月报 HTML 生成
# ============================================================

def generate_monthly_html(analyses, month_str):
    """生成月报 HTML。analyses: list of analysis dicts"""
    period = month_str

    # 合并所有周的数据
    all_insights = []
    all_trends = []
    all_apps = []
    all_opportunities = []
    all_tldr = []
    total_articles = 0

    for analysis in analyses:
        all_insights.extend(analysis.get("rtc_insights", []))
        all_trends.extend(analysis.get("trend_signals", []))
        all_apps.extend(analysis.get("app_discoveries", []))
        all_opportunities.extend(analysis.get("business_opportunities", []))
        all_tldr.extend(analysis.get("tldr", []))
        total_articles += analysis.get("meta", {}).get("article_count", 0)

    # App 去重
    seen_apps = set()
    unique_apps = []
    for app in all_apps:
        if app.get("name") not in seen_apps:
            seen_apps.add(app.get("name"))
            unique_apps.append(app)

    # RTC 相关统计
    rtc_insights = [i for i in all_insights if any(t in RTC_TRACKS for t in i.get("tags", []))]
    rtc_apps = [a for a in unique_apps if a.get("track", "") in RTC_TRACKS]

    # --- Header ---
    header = f'''
    <div class="page-header">
        <h1>📡 RTC 实时互动洞察月报</h1>
        <div class="subtitle">腾讯实时互动 · 出海趋势追踪 · 月度深度报告</div>
        <div class="meta">
            <span class="meta-item">📄 {total_articles} 篇文章</span>
            <span class="meta-item">📅 {len(analyses)} 个周期</span>
            <span class="meta-item">📡 {len(all_insights)} 条洞察</span>
            <span class="meta-item">📱 {len(unique_apps)} 个 App</span>
        </div>
        <div class="period">{html_escape(period)}</div>
    </div>
    <div class="container">
    '''

    # --- Stats ---
    stats = '<div class="stats-row">'
    stats += build_stat_card(total_articles, "分析文章总数")
    stats += build_stat_card(len(analyses), "覆盖周数")
    stats += build_stat_card(len(all_insights), "RTC 洞察总计", is_rtc=True)
    stats += build_stat_card(len(unique_apps), "累计发现 App")
    stats += build_stat_card(len(rtc_apps), "RTC 关联 App", is_rtc=True)
    stats += build_stat_card(len(all_opportunities), "商机线索")
    stats += '</div>'

    # --- 月度 TL;DR ---
    tldr_html = '<div class="tldr-box"><div class="tldr-title">⚡ 月度核心速览</div>'
    for item in all_tldr[:12]:
        tldr_html += f'<div class="tldr-item"><span class="arrow">→</span><span>{html_escape(item)}</span></div>'
    tldr_html += '</div>'

    # --- 深度洞察（按赛道分组）---
    insights_by_track = defaultdict(list)
    for insight in all_insights:
        for tag in insight.get("tags", ["其他"]):
            insights_by_track[tag].append(insight)

    insights_html = '<div class="section"><div class="section-title"><span class="icon">🔍</span> 赛道深度洞察</div>'
    # 先展示 RTC 相关赛道
    sorted_tracks = sorted(insights_by_track.keys(),
                           key=lambda t: (0 if t in RTC_TRACKS else 1, TRACK_PRIORITY.get(t, 99)))

    for track in sorted_tracks:
        track_insights = insights_by_track[track]
        is_rtc = track in RTC_TRACKS
        icon = TRACK_ICONS.get(track, "📌")
        color = TRACK_COLORS.get(track, "#636e72")

        border_style = f"border-left:3px solid {color};" if not is_rtc else f"border-left:3px solid var(--cyan);box-shadow:0 0 8px var(--rtc-glow);"
        insights_html += f'''
        <div style="margin-bottom:20px;padding:16px;background:var(--surface2);border-radius:10px;{border_style}">
            <h3 style="font-size:16px;margin-bottom:12px;">
                {icon} {html_escape(track)}
                {"<span class='rtc-badge'>核心赛道</span>" if is_rtc else ""}
                <span style="font-size:12px;color:var(--text2);margin-left:8px;">{len(track_insights)} 条洞察</span>
            </h3>'''

        for insight in track_insights[:4]:
            meta = ""
            if insight.get("judgment"):
                meta += f'<span style="font-size:12px;color:var(--orange);margin-right:12px;">💡 {html_escape(insight["judgment"])}</span>'
            if insight.get("opportunity"):
                meta += f'<span style="font-size:12px;color:var(--green);">🎯 {html_escape(insight["opportunity"])}</span>'

            insights_html += f'''
            <div style="padding:10px 0;border-bottom:1px solid var(--border);">
                <div style="font-size:14px;font-weight:500;">{html_escape(insight.get("title", ""))}</div>
                <div style="font-size:13px;color:var(--text2);margin-top:4px;line-height:1.6;">{html_escape(insight.get("body", "")[:300])}</div>
                <div style="margin-top:6px;">{meta}</div>
            </div>'''

        insights_html += '</div>'
    insights_html += '</div>'

    # --- 趋势信号汇总 ---
    trends_html = '<div class="section"><div class="section-title"><span class="icon">📈</span> 月度趋势信号汇总</div>'
    for direction in ["rising", "emerging", "falling"]:
        dir_trends = [t for t in all_trends if t.get("direction") == direction]
        if not dir_trends:
            continue
        dir_labels = {"rising": "🟢 强势升温", "emerging": "🟡 新兴/值得关注", "falling": "🔴 降温/风险"}
        trends_html += f'<h4 style="font-size:14px;color:var(--text2);margin:16px 0 8px;">{dir_labels.get(direction)}</h4>'
        for t in dir_trends:
            trends_html += f'''
            <div class="trend-signal">
                {build_direction_icon(direction)}
                <div>
                    <div>{html_escape(t.get("signal", ""))}</div>
                    <div class="evidence">{html_escape(t.get("evidence", ""))}</div>
                </div>
            </div>'''
    trends_html += '</div>'

    # --- App 发现汇总 ---
    apps_html = '<div class="section"><div class="section-title"><span class="icon">📱</span> 本月新发现 App</div>'

    # 按赛道分组
    apps_by_track = defaultdict(list)
    for app in unique_apps:
        apps_by_track[app.get("track", "其他")].append(app)

    sorted_app_tracks = sorted(apps_by_track.keys(),
                               key=lambda t: (0 if t in RTC_TRACKS else 1, TRACK_PRIORITY.get(t, 99)))

    for track in sorted_app_tracks:
        track_apps = apps_by_track[track]
        is_rtc = track in RTC_TRACKS
        icon = TRACK_ICONS.get(track, "📌")
        color = TRACK_COLORS.get(track, "#636e72")

        apps_html += f'''
        <h4 style="font-size:14px;margin:16px 0 8px;color:{color};">
            {icon} {html_escape(track)} ({len(track_apps)})
            {"<span class='rtc-badge'>RTC</span>" if is_rtc else ""}
        </h4>'''
        apps_html += '<table class="data-table"><thead><tr><th>App</th><th>描述</th><th>RTC关联</th><th>市场</th></tr></thead><tbody>'
        for app in track_apps:
            apps_html += f'''<tr>
                <td><strong style="color:var(--accent2);">{html_escape(app.get("name", ""))}</strong></td>
                <td style="font-size:12px;">{html_escape(app.get("description", ""))}</td>
                <td style="font-size:12px;color:var(--cyan);">{html_escape(app.get("rtc_relevance", "-"))}</td>
                <td style="font-size:12px;">{html_escape(app.get("market", "-"))}</td>
            </tr>'''
        apps_html += '</tbody></table>'
    apps_html += '</div>'

    # --- 商机汇总 ---
    opp_html = '<div class="section"><div class="section-title"><span class="icon">💰</span> 月度商机沉淀</div>'
    sorted_opps = sorted(all_opportunities, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("urgency", ""), 3))
    for opp in sorted_opps:
        opp_html += build_biz_opp(opp)
    opp_html += '</div>'

    # --- 赛道热度分布 ---
    track_counter = Counter()
    for analysis in analyses:
        for cls in analysis.get("article_classifications", []):
            for t in cls.get("tracks", []):
                track_counter[t] += 1

    if track_counter:
        chart_data = [(t, c, TRACK_COLORS.get(t, "#636e72")) for t, c in track_counter.most_common()]
        chart_html = f'<div class="section"><div class="section-title"><span class="icon">📊</span> 赛道热度分布</div>'
        chart_html += build_bar_chart(chart_data)
        chart_html += '</div>'
    else:
        chart_html = ""

    # --- Footer ---
    footer = f'''
    <div class="page-footer">
        RTC 实时互动洞察追踪系统 · 月报 · 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")} · Powered by Claude AI
    </div>
    </div>'''

    body = header + stats + tldr_html + insights_html + trends_html + apps_html + opp_html + chart_html + footer
    return wrap_html_page(f"RTC 月报 | {period}", body)


# ============================================================
# 门户页生成
# ============================================================

def generate_portal_html(reports_info):
    """
    生成门户页（Tab切换）
    reports_info: list of {"type": "weekly"|"monthly", "period": "...", "filepath": "...", "label": "..."}
    """
    # 计算汇总数据
    total_articles = 0
    total_apps = set()
    total_periods = 0
    for report in reports_info:
        if os.path.exists(report["filepath"]):
            # 尝试从对应 analysis 文件中获取统计
            period = report.get("period", "")
            analysis_file = os.path.join(ANALYSIS_DIR, f"analysis_{period}.json")
            if os.path.exists(analysis_file):
                try:
                    with open(analysis_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    total_articles += data.get("meta", {}).get("article_count", 0)
                    for app in data.get("app_discoveries", []):
                        total_apps.add(app.get("name", ""))
                    total_periods += 1
                except Exception:
                    total_periods += 1
            else:
                total_periods += 1

    generated_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 页面头部 — 精美大标题
    header = f'''
    <div class="page-header">
        <h1>📡 RTC 实时互动洞察中心</h1>
        <div class="subtitle">腾讯实时互动 · 出海趋势追踪 · 周报月报一站式浏览</div>
        <div class="meta">
            <span class="meta-item">📅 {total_periods} 个报告周期</span>
            <span class="meta-item">📄 {total_articles} 篇文章</span>
            <span class="meta-item">📱 {len(total_apps)} 个 App</span>
            <span class="meta-item">🕐 {generated_time}</span>
        </div>
    </div>
    '''

    # Tab 导航
    tab_nav = '<div class="tab-nav">'
    tab_contents = ""

    for i, report in enumerate(reports_info):
        tab_id = f"tab-{report['type']}-{i}"
        active = " active" if i == 0 else ""
        btn_cls = "tab-btn monthly" if report["type"] == "monthly" else "tab-btn"

        tab_nav += f'<button class="{btn_cls}{active}" data-tab="{tab_id}" onclick="switchTab(\'{tab_id}\')">{html_escape(report["label"])}</button>'

        # 读取报告内容（提取 body 部分）
        if os.path.exists(report["filepath"]):
            with open(report["filepath"], "r", encoding="utf-8") as f:
                content = f.read()
            # 提取 <body> 内容
            body_match = re.search(r'<body>(.*?)</body>', content, re.DOTALL)
            if body_match:
                inner = body_match.group(1)
            else:
                inner = content
        else:
            inner = f'<div class="container"><p>报告文件不存在: {html_escape(report["filepath"])}</p></div>'

        tab_contents += f'<div id="{tab_id}" class="tab-content{active}">{inner}</div>'

    tab_nav += '</div>'

    body = header + tab_nav + tab_contents + PORTAL_JS
    return wrap_html_page("RTC 实时互动洞察中心", body)


# ============================================================
# 命令行入口
# ============================================================

def cmd_weekly(args):
    """生成周报"""
    period = args.period
    if not period:
        print("[错误] 请指定 --period，格式: 2026-03-09_2026-03-15")
        return

    print(f"\n生成周报: {period}")
    analysis = load_analysis(period)
    if not analysis:
        return

    articles_data = load_articles(period)

    # 更新 App 追踪
    tracker = update_app_tracker_from_analysis(analysis)
    print(f"  App 追踪已更新: {len(tracker['apps'])} 个 App")

    # 生成 HTML
    html = generate_weekly_html(analysis, articles_data)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, f"weekly_{period}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [输出] 周报: {filepath}")


def cmd_monthly(args):
    """生成月报"""
    month = args.month
    if not month:
        print("[错误] 请指定 --month，格式: 2026-03")
        return

    print(f"\n生成月报: {month}")

    # 查找该月所有分析文件
    pattern = os.path.join(ANALYSIS_DIR, f"analysis_{month}*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"  [错误] 未找到 {month} 的分析文件")
        print(f"  请确认 {ANALYSIS_DIR}/ 目录下有 analysis_{month}*.json 文件")
        return

    analyses = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            if data.get("tldr"):
                analyses.append(data)
                print(f"  加载: {os.path.basename(f)}")

    if not analyses:
        print("  [错误] 所有分析文件内容为空")
        return

    html = generate_monthly_html(analyses, month)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, f"monthly_{month}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [输出] 月报: {filepath}")


def cmd_portal(args):
    """生成门户页"""
    print("\n生成门户页...")

    # 扫描 output 目录下的报告文件
    reports = []

    # 月报
    monthly_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "monthly_*.html")), reverse=True)
    for f in monthly_files:
        basename = os.path.basename(f)
        month = basename.replace("monthly_", "").replace(".html", "")
        reports.append({
            "type": "monthly",
            "period": month,
            "filepath": f,
            "label": f"📊 月报 {month}",
        })

    # 周报
    weekly_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "weekly_*.html")), reverse=True)
    for f in weekly_files:
        basename = os.path.basename(f)
        period = basename.replace("weekly_", "").replace(".html", "")
        reports.append({
            "type": "weekly",
            "period": period,
            "filepath": f,
            "label": f"📡 周报 {period}",
        })

    if not reports:
        print("  [错误] output/ 目录下没有找到报告文件")
        print("  请先生成周报或月报")
        return

    html = generate_portal_html(reports)
    filepath = os.path.join(OUTPUT_DIR, "portal.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [输出] 门户页: {filepath}")
    print(f"  包含 {len(reports)} 个报告 Tab")


def main():
    parser = argparse.ArgumentParser(description="RTC 实时互动洞察追踪 - 报告生成")
    subparsers = parser.add_subparsers(dest="command", help="报告类型")

    # 周报
    weekly_parser = subparsers.add_parser("weekly", help="生成周报")
    weekly_parser.add_argument("--period", required=True, help="时间范围，格式: 2026-03-09_2026-03-15")

    # 月报
    monthly_parser = subparsers.add_parser("monthly", help="生成月报")
    monthly_parser.add_argument("--month", required=True, help="月份，格式: 2026-03")

    # 门户
    subparsers.add_parser("portal", help="生成门户页")

    args = parser.parse_args()

    if args.command == "weekly":
        cmd_weekly(args)
    elif args.command == "monthly":
        cmd_monthly(args)
    elif args.command == "portal":
        cmd_portal(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
