#!/usr/bin/env python3
"""
AI HOT 定时推送脚本
定时从 aihot.virxact.com 拉取精选 AI 资讯，推送到企业微信群
"""

import os
import sys
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Dict
from urllib.parse import urlparse

# ========== 配置 ==========
WECOM_WEBHOOK_URL = os.environ.get("WECOM_WEBHOOK_URL")
if not WECOM_WEBHOOK_URL:
    print("Error: WECOM_WEBHOOK_URL environment variable not set")
    sys.exit(1)

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 aihot-skill/0.2.0"
BASE_URL = "https://aihot.virxact.com"
TAKE_COUNT = 6   # 每次推送精选条数（企业微信 markdown 上限 4096 字符）


def get_recent_items(hours: int = 24, limit: int = TAKE_COUNT) -> List[Dict]:
    """拉取最近 N 小时的精选 AI 动态"""
    since = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(hours=hours)
    since_str = since.strftime("%Y-%m-%dT%H:%M:%SZ")

    url = f"{BASE_URL}/api/public/items?mode=selected&since={since_str}&take={limit}"
    print(f"[{datetime.now()}] 请求 URL: {url}")

    resp = requests.get(url, headers={"User-Agent": UA}, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    items = data.get("items", [])
    print(f"[{datetime.now()}] 获取到 {len(items)} 条精选动态")
    return items


def time_ago(published_at: str) -> str:
    """将 ISO 时间转换为'XX小时前'格式"""
    try:
        pub_time = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    except ValueError:
        return ""

    now = datetime.now(timezone.utc)
    diff_seconds = int((now - pub_time).total_seconds())

    if diff_seconds < 0:
        return "刚刚"
    elif diff_seconds < 3600:
        minutes = diff_seconds // 60
        return f"{minutes}分钟前" if minutes > 0 else "刚刚"
    elif diff_seconds < 86400:
        hours = diff_seconds // 3600
        return f"{hours}小时前"
    else:
        days = diff_seconds // 86400
        return f"{days}天前"


def format_category(category: str) -> str:
    """将英文分类转为中文"""
    mapping = {
        "ai-models": "🤖 模型发布",
        "ai-products": "🆕 产品更新",
        "industry": "📊 行业动态",
        "paper": "📄 论文研究",
        "tip": "💡 技巧观点",
    }
    return mapping.get(category, "📌 其他")


def format_markdown(items: List[Dict], push_time: str) -> str:
    """格式化为企业微信 markdown 内容"""
    if not items:
        return f"**📭 AI HOT · {push_time}**\n\n过去 24 小时暂无精选 AI 动态"

    lines = [
        f"**🤖 AI HOT · {push_time}**（{len(items)} 条精选 · 24小时内）",
        ""
    ]

    for i, item in enumerate(items, 1):
        title = item.get("title", "无标题")
        source = item.get("source", "未知来源")
        summary = item.get("summary", "")
        url = item.get("url", "")
        ago = time_ago(item.get("publishedAt", ""))
        category = format_category(item.get("category", ""))

        lines.append(f"**{i}. {title}**")
        lines.append(f"{category} · {source} · {ago}")

        if summary:
            # 摘要限制在 100 字以内，避免超出企业微信 4096 字符上限
            summary_clean = summary.replace("\n", " ").strip()
            if len(summary_clean) > 100:
                summary_clean = summary_clean[:100] + "..."
            lines.append(f"{summary_clean}")

        if url:
            # 链接仅显示域名，完整 URL 太长会超出上限
            domain = urlparse(url).netloc if url else ""
            path = urlparse(url).path if url else ""
            lines.append(f"🔗 {domain}{path}")

        lines.append("")  # 每条之间空行

    lines.append("---")
    lines.append(f"🌐 数据来源：aihot.virxact.com")

    return "\n".join(lines)


def send_markdown(content: str) -> None:
    """发送到企业微信群"""
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }

    resp = requests.post(WECOM_WEBHOOK_URL, json=payload, timeout=30)
    result = resp.json()

    if result.get("errcode") != 0:
        print(f"[{datetime.now()}] 发送失败: {result}")
        raise Exception(f"企业微信 API 返回错误: {result}")
        sys.exit(1)

    print(f"[{datetime.now()}] 推送成功！")


def main():
    print(f"[{datetime.now()}] ========== AI HOT 定时推送开始 ==========")

    # 推3个时间点：北京 9:00、12:00、18:00
    hour = datetime.now().hour
    if hour == 9:
        push_time = "早间精选"
    elif hour == 12:
        push_time = "午间精选"
    elif hour == 18:
        push_time = "晚间精选"
    else:
        push_time = f"{hour}:00"

    # 拉取数据
    items = get_recent_items(hours=24, limit=TAKE_COUNT)

    # 格式化并发送
    content = format_markdown(items, push_time)
    print(f"[{datetime.now()}] 消息总长度：{len(content)} 字符")
    print(f"[{datetime.now()}] 消息内容预览：\n{content[:500]}...")

    send_markdown(content)
    print(f"[{datetime.now()}] ========== AI HOT 定时推送完成 ==========")


if __name__ == "__main__":
    main()
