#!/usr/bin/env python3
"""
RTC 实时互动洞察追踪系统 - 文章抓取脚本

Step 1: 从 WeWe RSS 抓取公众号文章 → 存为结构化 JSON → 生成 AI 分析 Prompt

用法：
    python3 fetch_articles.py                    # 抓取本周文章
    python3 fetch_articles.py --days 14          # 抓取最近14天文章
    python3 fetch_articles.py --start 2026-03-01 --end 2026-03-15
"""

import requests
import json
import re
import os
import sys
import argparse
import sqlite3
from datetime import datetime, timedelta
from html.parser import HTMLParser
from collections import Counter, defaultdict

from config import (
    WEWE_RSS_BASE_URL, AUTH_CODE, DATA_DIR, OUTPUT_DIR,
    ARTICLES_DIR, PROMPTS_DIR, ANALYSIS_DIR, DATE_FILTER_START,
    TRACK_KEYWORDS, MARKET_KEYWORDS, FILTER_KEYWORDS,
    ANALYSIS_PROMPT_TEMPLATE,
    ARTICLE_EXCERPT_LENGTH, PROMPT_BATCH_SIZE,
)


# ============================================================
# HTML 解析工具
# ============================================================

class HTMLTextExtractor(HTMLParser):
    SKIP_TAGS = {'style', 'script', 'noscript'}

    def __init__(self):
        super().__init__()
        self.result = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag.lower() in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            text = data.strip()
            if text:
                self.result.append(text)

    def get_text(self):
        return " ".join(self.result)


def html_to_text(html_str):
    if not html_str:
        return ""
    extractor = HTMLTextExtractor()
    try:
        extractor.feed(html_str)
        return extractor.get_text()
    except Exception:
        return html_str


# ============================================================
# 日期处理
# ============================================================

def parse_date(date_str):
    if not date_str:
        return None
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def format_date(date_str):
    d = parse_date(date_str)
    if d:
        return d.strftime("%Y-%m-%d")
    return date_str or "未知"


# ============================================================
# 文章分析（基础关键词匹配，AI 分析前的预处理）
# ============================================================

def detect_tracks(text):
    text_upper = text.upper()
    tracks = []
    for track, keywords in TRACK_KEYWORDS.items():
        for kw in keywords:
            if kw.upper() in text_upper:
                tracks.append(track)
                break
    return tracks if tracks else ["其他出海赛道"]


def detect_markets(text):
    markets = []
    for market, keywords in MARKET_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                markets.append(market)
                break
    return markets if markets else ["未明确"]


def should_filter_article(title):
    for kw in FILTER_KEYWORDS:
        if kw in title:
            return True
    return False


# ============================================================
# WeWe RSS 数据获取
# ============================================================

def get_feeds_list():
    url = f"{WEWE_RSS_BASE_URL}/feeds"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"  [错误] 获取订阅列表失败: {e}")
    return None


def fetch_feed_content(feed_id):
    url = f"{WEWE_RSS_BASE_URL}/feeds/{feed_id}.json"
    params = {"limit": "500"}
    if AUTH_CODE:
        params["key"] = AUTH_CODE
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"  [错误] 获取 feed {feed_id} 异常: {e}")
    return None


def fetch_articles_from_db(start_date, end_date):
    """从 SQLite 数据库直接读取文章"""
    db_path = os.path.join(DATA_DIR, "wewe-rss.db")
    if not os.path.exists(db_path):
        return []

    articles = []
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """SELECT id, mpName, title, picUrl, publishTime, link
               FROM articles
               WHERE publishTime >= ? AND publishTime <= ?
               ORDER BY publishTime DESC""",
            (start_date, end_date + " 23:59:59")
        )

        for row in cursor.fetchall():
            articles.append({
                "id": row["id"],
                "title": row["title"],
                "source": row["mpName"],
                "link": row["link"] or "",
                "pub_date": row["publishTime"],
                "pic_url": row["picUrl"] or "",
                "content": "",
            })

        conn.close()
    except Exception as e:
        print(f"  [错误] 读取数据库失败: {e}")

    return articles


def fetch_article_content_via_api(feed_id):
    """通过 WeWe RSS API 获取文章全文"""
    data = fetch_feed_content(feed_id)
    if not data:
        return []

    articles = []
    source_name = data.get("title", "未知来源")
    for item in data.get("items", []):
        content_html = item.get("content_html", "")
        content_text = html_to_text(content_html) if content_html else item.get("content_text", "")

        articles.append({
            "title": item.get("title", ""),
            "link": item.get("url", ""),
            "content": content_text,
            "content_html": content_html,
            "pub_date": item.get("date_published", "") or item.get("date_modified", ""),
            "source": source_name,
        })
    return articles


# ============================================================
# 核心：抓取并处理文章
# ============================================================

def fetch_all_articles(start_date, end_date):
    """抓取所有文章，优先用 API 获取全文，回退到数据库"""
    print(f"\n{'='*60}")
    print(f"  RTC 实时互动洞察追踪 - 文章抓取")
    print(f"  时间范围: {start_date} ~ {end_date}")
    print(f"  数据源: {WEWE_RSS_BASE_URL}")
    print(f"{'='*60}")

    # 尝试通过 API 获取
    print("\n[1/3] 获取订阅列表...")
    feeds = get_feeds_list()

    all_articles = []

    if feeds:
        print(f"  找到 {len(feeds)} 个订阅源")
        print("\n[2/3] 抓取文章全文...")
        for feed in feeds:
            feed_id = feed.get("id", "")
            feed_name = feed.get("mpName", feed_id)
            print(f"  抓取: {feed_name} ...", end=" ")

            articles = fetch_article_content_via_api(feed_id)
            if articles:
                # 按日期过滤
                filtered = []
                for a in articles:
                    d = parse_date(a.get("pub_date", ""))
                    if d:
                        d_naive = d.replace(tzinfo=None) if d.tzinfo else d
                        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                        if start_dt <= d_naive < end_dt:
                            filtered.append(a)
                print(f"{len(filtered)}/{len(articles)} 篇在时间范围内")
                all_articles.extend(filtered)
            else:
                print("失败")
    else:
        print("  [提示] 无法连接 WeWe RSS API，尝试从数据库读取...")
        print("\n[2/3] 从数据库读取文章...")
        all_articles = fetch_articles_from_db(start_date, end_date)
        if all_articles:
            print(f"  从数据库读取到 {len(all_articles)} 篇文章")
        else:
            print("  [警告] 数据库中也没有找到文章")
            return []

    # 去重（按标题）
    seen_titles = set()
    unique_articles = []
    for a in all_articles:
        title = a.get("title", "")
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(a)

    # 过滤
    filtered_articles = [a for a in unique_articles if not should_filter_article(a.get("title", ""))]

    print(f"\n[3/3] 文章处理...")
    print(f"  总抓取: {len(all_articles)} → 去重: {len(unique_articles)} → 过滤后: {len(filtered_articles)}")

    # 基础分析（关键词匹配）
    for article in filtered_articles:
        full_text = article.get("title", "") + " " + article.get("content", "")
        article["tracks"] = detect_tracks(full_text)
        article["markets"] = detect_markets(full_text)
        article["date_formatted"] = format_date(article.get("pub_date", ""))

    # 按日期排序
    filtered_articles.sort(key=lambda x: x.get("date_formatted", ""), reverse=True)

    return filtered_articles


# ============================================================
# 输出：保存文章 JSON + 生成 Prompt
# ============================================================

def save_articles_json(articles, start_date, end_date):
    """保存文章为结构化 JSON"""
    os.makedirs(ARTICLES_DIR, exist_ok=True)

    filename = f"articles_{start_date}_{end_date}.json"
    filepath = os.path.join(ARTICLES_DIR, filename)

    # 统计
    track_counter = Counter()
    market_counter = Counter()
    for a in articles:
        for t in a.get("tracks", []):
            track_counter[t] += 1
        for m in a.get("markets", []):
            market_counter[m] += 1

    output = {
        "meta": {
            "period": f"{start_date} ~ {end_date}",
            "fetched_at": datetime.now().isoformat(),
            "article_count": len(articles),
            "source": "WeWe RSS",
        },
        "stats": {
            "tracks": dict(track_counter.most_common()),
            "markets": dict(market_counter.most_common()),
        },
        "articles": [
            {
                "title": a.get("title", ""),
                "source": a.get("source", ""),
                "link": a.get("link", ""),
                "date": a.get("date_formatted", ""),
                "tracks": a.get("tracks", []),
                "markets": a.get("markets", []),
                "content": a.get("content", ""),  # 保留全文供 AI 分析
            }
            for a in articles
        ],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n  [保存] 文章 JSON: {filepath}")
    return filepath


def generate_prompt_file(articles, start_date, end_date):
    """生成 AI 分析用的 Prompt 文件"""
    os.makedirs(PROMPTS_DIR, exist_ok=True)

    period = f"{start_date} ~ {end_date}"

    # 构建文章内容（每篇取标题 + 前 N 字）
    excerpt_len = ARTICLE_EXCERPT_LENGTH
    article_summaries = []
    for i, a in enumerate(articles, 1):
        content = a.get("content", "")
        excerpt = content[:excerpt_len] + "..." if len(content) > excerpt_len else content
        article_summaries.append(
            f"### 文章 {i}: {a.get('title', '无标题')}\n"
            f"- 来源: {a.get('source', '未知')}\n"
            f"- 日期: {a.get('date_formatted', '未知')}\n"
            f"- 预分类赛道: {', '.join(a.get('tracks', []))}\n"
            f"- 预分类市场: {', '.join(a.get('markets', []))}\n"
            f"- 正文:\n{excerpt}\n"
        )

    articles_text = "\n".join(article_summaries)

    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        period=period,
        articles=articles_text,
        article_count=len(articles),
    )

    # 如果文章太多，分批生成 Prompt
    if len(articles) > PROMPT_BATCH_SIZE:
        print(f"\n  [提示] 文章数({len(articles)})较多，将分批生成 Prompt")
        batch_num = 0
        for i in range(0, len(articles), PROMPT_BATCH_SIZE):
            batch_num += 1
            batch = articles[i:i + PROMPT_BATCH_SIZE]
            batch_summaries = []
            for j, a in enumerate(batch, i + 1):
                content = a.get("content", "")
                excerpt = content[:excerpt_len] + "..." if len(content) > excerpt_len else content
                batch_summaries.append(
                    f"### 文章 {j}: {a.get('title', '无标题')}\n"
                    f"- 来源: {a.get('source', '未知')}\n"
                    f"- 日期: {a.get('date_formatted', '未知')}\n"
                    f"- 正文:\n{excerpt}\n"
                )
            batch_prompt = ANALYSIS_PROMPT_TEMPLATE.format(
                period=period,
                articles="\n".join(batch_summaries),
                article_count=len(batch),
            )
            filename = f"prompt_{start_date}_{end_date}_batch{batch_num}.md"
            filepath = os.path.join(PROMPTS_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(batch_prompt)
            print(f"  [保存] Prompt 批次{batch_num}: {filepath}")
    else:
        filename = f"prompt_{start_date}_{end_date}.md"
        filepath = os.path.join(PROMPTS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"  [保存] Prompt: {filepath}")

    # 同时保存一份 analysis 模板
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    template_path = os.path.join(ANALYSIS_DIR, f"analysis_{start_date}_{end_date}.json")
    if not os.path.exists(template_path):
        template = {
            "meta": {
                "period": period,
                "article_count": len(articles),
                "analyzed_at": "",
            },
            "tldr": [],
            "rtc_insights": [],
            "trend_signals": [],
            "app_discoveries": [],
            "business_opportunities": [],
            "article_classifications": [],
        }
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        print(f"  [保存] 分析模板: {template_path}")

    return filepath


def print_summary(articles):
    """打印抓取结果摘要"""
    if not articles:
        print("\n  [结果] 未找到文章")
        return

    track_counter = Counter()
    market_counter = Counter()
    for a in articles:
        for t in a.get("tracks", []):
            track_counter[t] += 1
        for m in a.get("markets", []):
            market_counter[m] += 1

    print(f"\n{'='*60}")
    print(f"  抓取完成！共 {len(articles)} 篇文章")
    print(f"{'='*60}")

    print(f"\n  赛道分布:")
    for track, count in track_counter.most_common():
        bar = "█" * min(count, 30)
        print(f"    {track:16s} {bar} ({count})")

    print(f"\n  市场分布:")
    for market, count in market_counter.most_common(8):
        bar = "█" * min(count, 30)
        print(f"    {market:8s} {bar} ({count})")

    print(f"\n  来源分布:")
    source_counter = Counter(a.get("source", "未知") for a in articles)
    for source, count in source_counter.most_common():
        print(f"    {source:16s} {count} 篇")

    print(f"\n  下一步:")
    print(f"  1. 查看 {PROMPTS_DIR}/ 目录下的 Prompt 文件")
    print(f"  2. 在 CodeBuddy 中让 Claude 读取 Prompt 并输出分析 JSON")
    print(f"  3. 将分析结果保存到 {ANALYSIS_DIR}/ 目录")
    print(f"  4. 运行 python3 generate_report.py 生成报告")
    print(f"{'='*60}")


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="RTC 实时互动洞察追踪 - 文章抓取")
    parser.add_argument("--start", help="开始日期 (YYYY-MM-DD)")
    parser.add_argument("--end", help="结束日期 (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, default=7, help="抓取最近N天 (默认7天)")
    args = parser.parse_args()

    if args.start and args.end:
        start_date = args.start
        end_date = args.end
    else:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    # 确保目录存在
    for d in [ARTICLES_DIR, PROMPTS_DIR, ANALYSIS_DIR, OUTPUT_DIR]:
        os.makedirs(d, exist_ok=True)

    # 抓取
    articles = fetch_all_articles(start_date, end_date)

    if not articles:
        print("\n[结果] 未抓取到文章，请检查：")
        print("  1. WeWe RSS 是否在运行 (docker compose up -d)")
        print("  2. 是否已添加公众号订阅")
        print("  3. 时间范围是否正确")
        return

    # 保存
    save_articles_json(articles, start_date, end_date)
    generate_prompt_file(articles, start_date, end_date)
    print_summary(articles)


if __name__ == "__main__":
    main()
