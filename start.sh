#!/bin/bash
# ============================================================
# RTC 实时互动洞察追踪系统 - 一键启动脚本
# ============================================================

set -e

echo "=========================================="
echo "  📡 RTC 实时互动洞察追踪系统"
echo "=========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Step 1: 检查 Docker
echo ""
echo -e "${GREEN}[Step 1/4]${NC} 检查 Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[错误] Docker 未安装${NC}"
    echo "  macOS: brew install --cask docker"
    exit 1
fi

if ! docker info &> /dev/null 2>&1; then
    echo -e "${RED}[错误] Docker 未运行，请先启动 Docker Desktop${NC}"
    exit 1
fi
echo "  Docker 已就绪"

# Step 2: 创建目录结构
echo ""
echo -e "${GREEN}[Step 2/4]${NC} 创建目录结构..."
mkdir -p data/articles data/prompts data/analysis output
echo "  目录结构已创建:"
echo "    data/articles/   - 文章原文 JSON"
echo "    data/prompts/    - AI 分析 Prompt"
echo "    data/analysis/   - AI 分析结果 JSON"
echo "    output/          - HTML 报告输出"

# Step 3: 启动 WeWe RSS
echo ""
echo -e "${GREEN}[Step 3/4]${NC} 启动 WeWe RSS..."
docker compose up -d
echo "  等待服务启动..."
sleep 5

if curl -s http://localhost:4000 > /dev/null 2>&1; then
    echo -e "  WeWe RSS 已启动  访问: ${GREEN}http://localhost:4000${NC}"
else
    echo -e "${YELLOW}  [提示] 服务可能仍在启动中，请稍等后访问 http://localhost:4000${NC}"
fi

# Step 4: 工作流说明
echo ""
echo -e "${GREEN}[Step 4/4]${NC} 三步工作流:"
echo ""
echo -e "${CYAN}  Step 1 - 抓取文章:${NC}"
echo "    python3 fetch_articles.py              # 抓取最近7天文章"
echo "    python3 fetch_articles.py --days 14    # 抓取最近14天"
echo ""
echo -e "${CYAN}  Step 2 - AI 分析（推荐使用 Skill）:${NC}"
echo "    在 CodeBuddy 中使用 rtc-weekly-analysis Skill 自动完成分析"
echo "    或手动: 打开 data/prompts/ 下的 Prompt 文件，让 Claude 分析"
echo "    分析结果保存到 data/analysis/ 目录"
echo ""
echo -e "${CYAN}  Step 3 - 生成报告:${NC}"
echo "    python3 generate_report.py weekly --period 2026-03-09_2026-03-15"
echo "    python3 generate_report.py monthly --month 2026-03"
echo "    python3 generate_report.py portal"
echo ""
echo "=========================================="
echo "  系统已就绪！"
echo "=========================================="
