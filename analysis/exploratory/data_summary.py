#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探索性数据分析 - 数据概览
生成数据基础统计和质量报告
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import re

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


def load_all_posts():
    """加载所有有效的帖子数据并去重"""
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

    # AI/IT相关关键词
    ai_keywords = [
        'chatgpt', 'gpt', 'ai', '大模型', '人工智能', 'llm',
        '程序员', 'it', '开发', '失业', '岗位', '技能',
        '职业', 'programmer', 'developer', 'job', 'deepseek',
        'software engineer', 'coding', 'employment'
    ]

    for filename in valid_files:
        file_path = data_dir / filename
        if not file_path.exists():
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 统一为列表格式
            if isinstance(data, dict):
                data = [data]

            for post in data:
                url = post.get('url', '')

                # 去重
                if url and url in seen_urls:
                    continue

                # 检查相关性
                title = post.get('title', '').lower()
                content = post.get('content', '').lower()
                is_ai_related = any(kw in title or kw in content for kw in ai_keywords)

                if is_ai_related and url:
                    seen_urls.add(url)
                    all_posts.append(post)

        except Exception as e:
            print(f"⚠️  警告: 无法读取 {filename}: {e}")

    return all_posts


def analyze_basic_stats(posts):
    """基础统计分析"""
    stats = {
        'total_posts': len(posts),
        'total_comments': sum(p.get('comment_count', 0) for p in posts),
        'avg_comments': 0,
        'posts_with_100plus_comments': 0,
        'platforms': defaultdict(int),
        'time_distribution': defaultdict(int)
    }

    if stats['total_posts'] > 0:
        stats['avg_comments'] = stats['total_comments'] / stats['total_posts']

    for post in posts:
        # 评论数统计
        if post.get('comment_count', 0) >= 100:
            stats['posts_with_100plus_comments'] += 1

        # 平台分布
        platform = post.get('platform', 'unknown')
        stats['platforms'][platform] += 1

        # 时间分布（提取年份）
        created_at = post.get('created_at', '')
        year = extract_year(created_at)
        if year:
            stats['time_distribution'][year] += 1

    return stats


def extract_year(date_str):
    """从各种日期格式中提取年份"""
    if not date_str:
        return None

    # 匹配 2023, 2024, 2025 等
    match = re.search(r'(202[2-5])', str(date_str))
    if match:
        return match.group(1)

    return None


def analyze_content(posts):
    """内容分析"""
    all_titles = ' '.join([p.get('title', '') for p in posts])
    all_content = ' '.join([p.get('content', '')[:500] for p in posts])  # 只取前500字符

    # 关键词统计
    keywords = {
        'AI/ChatGPT': ['chatgpt', 'gpt', 'ai', '大模型', '人工智能'],
        '就业相关': ['失业', '岗位', '职业', 'job', 'employment', 'career'],
        '技能相关': ['技能', 'skill', '学习', 'learn', '转型'],
        '程序员': ['程序员', 'programmer', 'developer', '开发', 'coder']
    }

    keyword_counts = {}
    combined_text = (all_titles + ' ' + all_content).lower()

    for category, words in keywords.items():
        count = sum(combined_text.count(word) for word in words)
        keyword_counts[category] = count

    return keyword_counts


def generate_report(posts, stats, keywords):
    """生成分析报告"""
    output_dir = project_root / "outputs" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "data_summary.txt"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("大模型对IT行业影响 - 数据概览报告\n")
        f.write("=" * 80 + "\n\n")

        # 基础统计
        f.write("📊 基础统计\n")
        f.write("-" * 80 + "\n")
        f.write(f"总帖子数: {stats['total_posts']}\n")
        f.write(f"总评论数: {stats['total_comments']}\n")
        f.write(f"平均评论数: {stats['avg_comments']:.1f}\n")
        f.write(f"评论≥100的帖子数: {stats['posts_with_100plus_comments']}\n")
        f.write(f"距离作业要求(≥18): {'✅ 达标' if stats['posts_with_100plus_comments'] >= 18 else f'⚠️  还需{18 - stats['posts_with_100plus_comments']}个'}\n\n")

        # 平台分布
        f.write("📍 平台分布\n")
        f.write("-" * 80 + "\n")
        for platform, count in stats['platforms'].items():
            f.write(f"{platform}: {count}个帖子\n")
        f.write("\n")

        # 时间分布
        f.write("📅 时间分布\n")
        f.write("-" * 80 + "\n")
        for year in sorted(stats['time_distribution'].keys()):
            count = stats['time_distribution'][year]
            f.write(f"{year}年: {count}个帖子\n")
        f.write("\n")

        # 关键词统计
        f.write("🔑 关键词统计\n")
        f.write("-" * 80 + "\n")
        for category, count in keywords.items():
            f.write(f"{category}: {count}次提及\n")
        f.write("\n")

        # 帖子列表
        f.write("📝 帖子列表\n")
        f.write("-" * 80 + "\n")
        for i, post in enumerate(posts, 1):
            f.write(f"\n{i}. [{post.get('platform', 'N/A')}] {post.get('title', 'N/A')}\n")
            f.write(f"   评论数: {post.get('comment_count', 0)} | 时间: {post.get('created_at', 'N/A')}\n")
            f.write(f"   URL: {post.get('url', 'N/A')}\n")

    print(f"✅ 报告已生成: {report_path}")
    return report_path


def main():
    """主函数"""
    print("🔍 开始数据分析...")

    # 加载数据
    print("\n1️⃣ 加载数据...")
    posts = load_all_posts()
    print(f"   找到 {len(posts)} 个AI/IT相关帖子")

    # 基础统计
    print("\n2️⃣ 基础统计分析...")
    stats = analyze_basic_stats(posts)

    # 内容分析
    print("\n3️⃣ 内容关键词分析...")
    keywords = analyze_content(posts)

    # 生成报告
    print("\n4️⃣ 生成报告...")
    report_path = generate_report(posts, stats, keywords)

    # 打印摘要
    print("\n" + "=" * 80)
    print("📊 数据概览摘要")
    print("=" * 80)
    print(f"总帖子数: {stats['total_posts']}")
    print(f"符合要求(评论≥100): {stats['posts_with_100plus_comments']}")
    print(f"数据完整度: {stats['posts_with_100plus_comments']/18*100:.1f}%")
    print("\n详细报告已保存至:")
    print(f"  {report_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
