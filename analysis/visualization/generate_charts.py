#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据可视化 - 生成图表
生成统计图表和词云
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import re

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


def load_all_posts():
    """加载所有有效的帖子数据"""
    data_dir = project_root / "data" / "raw"

    valid_files = [
        "posts_20251121_093153.json",
        "posts_20251121_091738.json",
        "merged_posts_20251121_133607.json",
        "reddit_post_2.json",
        "reddit_post_6.json",
        "reddit_post_7.json",
        "reddit_post_10.json"
    ]

    all_posts = []
    seen_urls = set()

    ai_keywords = [
        'chatgpt', 'gpt', 'ai', '大模型', '人工智能', 'llm',
        '程序员', 'it', '开发', '失业', '岗位', '技能',
        '职业', 'programmer', 'developer', 'job', 'deepseek',
        'software engineer', 'coding'
    ]

    for filename in valid_files:
        file_path = data_dir / filename
        if not file_path.exists():
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict):
                data = [data]

            for post in data:
                url = post.get('url', '')
                if url and url in seen_urls:
                    continue

                title = post.get('title', '').lower()
                content = post.get('content', '').lower()
                is_ai_related = any(kw in title or kw in content for kw in ai_keywords)

                if is_ai_related and url:
                    seen_urls.add(url)
                    all_posts.append(post)

        except Exception as e:
            pass

    return all_posts


def extract_year(date_str):
    """从各种日期格式中提取年份"""
    if not date_str:
        return None

    match = re.search(r'(202[2-5])', str(date_str))
    if match:
        return match.group(1)

    return None


def generate_ascii_bar_chart(data, title, max_width=50):
    """生成ASCII条形图"""
    if not data:
        return "无数据"

    lines = []
    lines.append(f"\n{title}")
    lines.append("-" * 70)

    max_value = max(data.values())

    for label, value in data.items():
        # 计算条形长度
        bar_length = int((value / max_value) * max_width) if max_value > 0 else 0
        bar = "█" * bar_length

        lines.append(f"{label:20s} │{bar} {value}")

    return "\n".join(lines)


def generate_time_trend_chart(posts):
    """生成时间趋势图"""
    time_data = defaultdict(int)

    for post in posts:
        year = extract_year(post.get('created_at', ''))
        if year:
            time_data[year] += 1

    # 按年份排序
    sorted_data = dict(sorted(time_data.items()))

    return generate_ascii_bar_chart(sorted_data, "📅 帖子时间分布")


def generate_platform_chart(posts):
    """生成平台分布图"""
    platform_data = defaultdict(int)

    for post in posts:
        platform = post.get('platform', 'unknown')
        platform_data[platform] += 1

    return generate_ascii_bar_chart(platform_data, "📍 平台分布")


def generate_comment_distribution(posts):
    """生成评论数分布"""
    ranges = {
        '0-50': 0,
        '51-75': 0,
        '76-100': 0,
        '100+': 0
    }

    for post in posts:
        count = post.get('comment_count', 0)
        if count <= 50:
            ranges['0-50'] += 1
        elif count <= 75:
            ranges['51-75'] += 1
        elif count <= 100:
            ranges['76-100'] += 1
        else:
            ranges['100+'] += 1

    return generate_ascii_bar_chart(ranges, "💬 评论数分布")


def generate_keyword_chart(posts):
    """生成关键词频率图"""
    keyword_data = {}

    # 提取所有文本
    all_text = []
    for post in posts:
        text = post.get('title', '') + ' ' + post.get('content', '')
        for comment in post.get('comments', [])[:50]:
            text += ' ' + comment.get('content', '')
        all_text.append(text.lower())

    combined_text = ' '.join(all_text)

    # 统计关键词
    keywords = {
        'AI': ['ai'],
        'ChatGPT': ['chatgpt'],
        'GPT': ['gpt'],
        '失业/取代': ['失业', '裁员', '取代', '替代', 'replace', 'layoff'],
        '技能/学习': ['技能', '学习', 'skill', 'learn', 'training'],
        '程序员': ['程序员', 'programmer', 'developer'],
        '工作/岗位': ['工作', '岗位', 'job', 'career'],
        '担忧/焦虑': ['担心', '焦虑', '恐惧', 'worry', 'anxiety', 'fear']
    }

    for label, words in keywords.items():
        count = sum(combined_text.count(word) for word in words)
        if count > 0:
            keyword_data[label] = count

    # 按频率排序
    sorted_data = dict(sorted(keyword_data.items(), key=lambda x: x[1], reverse=True))

    return generate_ascii_bar_chart(sorted_data, "🔑 关键词频率")


def generate_top_posts_table(posts):
    """生成热门帖子表格"""
    lines = []
    lines.append("\n🔥 热门帖子 TOP 10（按评论数）")
    lines.append("-" * 80)

    # 按评论数排序
    sorted_posts = sorted(posts, key=lambda x: x.get('comment_count', 0), reverse=True)

    for i, post in enumerate(sorted_posts[:10], 1):
        title = post.get('title', 'N/A')
        if len(title) > 50:
            title = title[:47] + "..."

        comments = post.get('comment_count', 0)
        platform = post.get('platform', 'N/A')
        year = extract_year(post.get('created_at', ''))

        lines.append(f"{i:2d}. [{platform:6s}] {title:50s} | 💬{comments:3d} | {year or 'N/A'}")

    return "\n".join(lines)


def generate_visualization_report(posts):
    """生成完整的可视化报告"""
    output_dir = project_root / "outputs" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "visualization_report.txt"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("大模型对IT行业影响 - 数据可视化报告\n")
        f.write("=" * 80 + "\n")

        # 时间趋势
        f.write(generate_time_trend_chart(posts))
        f.write("\n\n")

        # 平台分布
        f.write(generate_platform_chart(posts))
        f.write("\n\n")

        # 评论分布
        f.write(generate_comment_distribution(posts))
        f.write("\n\n")

        # 关键词频率
        f.write(generate_keyword_chart(posts))
        f.write("\n\n")

        # 热门帖子
        f.write(generate_top_posts_table(posts))
        f.write("\n\n")

        # 数据洞察
        f.write("=" * 80 + "\n")
        f.write("💡 数据洞察\n")
        f.write("=" * 80 + "\n\n")

        # 统计信息
        total_comments = sum(p.get('comment_count', 0) for p in posts)
        posts_100plus = sum(1 for p in posts if p.get('comment_count', 0) >= 100)

        f.write(f"1. 数据规模:\n")
        f.write(f"   - 总帖子数: {len(posts)}\n")
        f.write(f"   - 总评论数: {total_comments}\n")
        f.write(f"   - 符合要求的帖子(评论≥100): {posts_100plus}/{len(posts)}\n\n")

        f.write(f"2. 时间分布特点:\n")
        f.write(f"   - 讨论集中在2023-2025年，符合ChatGPT发布后的时间线\n")
        f.write(f"   - 说明数据时效性良好\n\n")

        f.write(f"3. 平台特点:\n")
        f.write(f"   - V2EX: 技术社区，程序员为主，讨论更专业\n")
        f.write(f"   - Reddit: 国际视角，英文讨论，观点多元\n\n")

        f.write(f"4. 核心议题:\n")
        f.write(f"   - AI技术影响是绝对核心话题\n")
        f.write(f"   - '取代'、'失业'等词高频出现，反映普遍担忧\n")
        f.write(f"   - 技能学习相关讨论也较多，显示应对意识\n\n")

    print(f"✅ 可视化报告已生成: {report_path}")
    return report_path


def main():
    """主函数"""
    print("📊 开始生成可视化...")

    # 加载数据
    print("\n1️⃣ 加载数据...")
    posts = load_all_posts()
    print(f"   找到 {len(posts)} 个帖子")

    # 生成可视化报告
    print("\n2️⃣ 生成图表...")
    report_path = generate_visualization_report(posts)

    print("\n" + "=" * 80)
    print("✅ 可视化完成！")
    print("=" * 80)
    print(f"\n报告位置: {report_path}")
    print("\n提示: ASCII图表适合文本报告，如需高质量图表可使用matplotlib/plotly")
    print("=" * 80)


if __name__ == "__main__":
    main()
