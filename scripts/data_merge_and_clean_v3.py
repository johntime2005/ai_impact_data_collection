#!/usr/bin/env python3
"""数据合并与清洗脚本 v3 - 使用修复后的Reddit数据"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def clean_text(text: str) -> str:
    """清洗文本内容"""
    if not text:
        return ""

    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 移除特殊字符但保留中文和基本标点
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()


def parse_date(date_str: str) -> str:
    """解析日期字符串为标准格式"""
    if not date_str:
        return ""

    # 处理各种日期格式
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # 尝试提取年月日
    match = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', date_str)
    if match:
        return f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"

    return date_str


def standardize_reddit_post(post: dict) -> dict:
    """标准化Reddit帖子格式"""
    comments = []
    for c in post.get('comments', []):
        comments.append({
            'author': c.get('author', ''),
            'content': clean_text(c.get('content', '')),
            'upvotes': c.get('upvotes', 0),
            'created_at': parse_date(c.get('created_at', '')),
            'platform': 'reddit'
        })

    return {
        'id': f"reddit_{hash(post.get('url', '')) % 100000}",
        'platform': 'reddit',
        'title': clean_text(post.get('title', '')),
        'content': clean_text(post.get('content', '')),
        'author': post.get('author', ''),
        'url': post.get('url', ''),
        'created_at': parse_date(post.get('created_at', '')),
        'subreddit': post.get('subreddit', ''),
        'upvotes': post.get('upvotes', 0),
        'comment_count': len(comments),
        'comments': comments,
        'language': 'en'
    }


def standardize_v2ex_post(post: dict) -> dict:
    """标准化V2EX帖子格式"""
    comments = []
    for c in post.get('comments', []):
        comments.append({
            'author': c.get('author', ''),
            'content': clean_text(c.get('content', '')),
            'upvotes': c.get('upvotes', 0),
            'created_at': parse_date(c.get('created_at', '')),
            'platform': 'v2ex'
        })

    return {
        'id': f"v2ex_{post.get('id', hash(post.get('url', '')) % 100000)}",
        'platform': 'v2ex',
        'title': clean_text(post.get('title', '')),
        'content': clean_text(post.get('content', '')),
        'author': post.get('author', ''),
        'url': post.get('url', ''),
        'created_at': parse_date(post.get('created_at', '')),
        'node': post.get('node', ''),
        'upvotes': post.get('upvotes', 0),
        'comment_count': len(comments),
        'comments': comments,
        'language': 'zh'
    }


def main():
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("数据合并与清洗 v3")
    print("=" * 60)

    all_posts = []

    # 加载修复后的Reddit数据
    print("\n[1/4] 加载Reddit数据...")
    reddit_fixed_path = raw_dir / "reddit_posts_fixed.json"
    if reddit_fixed_path.exists():
        with open(reddit_fixed_path, 'r', encoding='utf-8') as f:
            reddit_posts = json.load(f)
        print(f"  ✓ 加载 {len(reddit_posts)} 个Reddit帖子")

        for post in reddit_posts:
            std_post = standardize_reddit_post(post)
            all_posts.append(std_post)

    # 加载V2EX数据
    print("\n[2/4] 加载V2EX数据...")
    v2ex_path = raw_dir / "v2ex_ai_impact_posts.json"
    if v2ex_path.exists():
        with open(v2ex_path, 'r', encoding='utf-8') as f:
            v2ex_posts = json.load(f)
        print(f"  ✓ 加载 {len(v2ex_posts)} 个V2EX帖子")

        for post in v2ex_posts:
            std_post = standardize_v2ex_post(post)
            all_posts.append(std_post)

    print(f"\n  总计: {len(all_posts)} 个帖子")

    # 提取所有评论
    print("\n[3/4] 提取评论数据...")
    all_comments = []
    for post in all_posts:
        for comment in post.get('comments', []):
            comment['post_id'] = post['id']
            comment['post_title'] = post['title']
            all_comments.append(comment)

    print(f"  ✓ 提取完成: {len(all_comments)} 条评论")

    # 生成统计信息
    print("\n[4/4] 生成统计信息...")

    platform_stats = defaultdict(lambda: {'posts': 0, 'comments': 0})
    year_stats = defaultdict(int)
    language_stats = defaultdict(int)

    for post in all_posts:
        platform = post['platform']
        platform_stats[platform]['posts'] += 1
        platform_stats[platform]['comments'] += len(post.get('comments', []))

        # 年份统计
        date_str = post.get('created_at', '')
        if date_str:
            year = date_str[:4]
            year_stats[year] += 1

        # 语言统计
        for comment in post.get('comments', []):
            lang = post.get('language', 'unknown')
            language_stats[lang] += 1

    statistics = {
        'total_posts': len(all_posts),
        'total_comments': len(all_comments),
        'avg_comments_per_post': round(len(all_comments) / len(all_posts), 1) if all_posts else 0,
        'platform_distribution': dict(platform_stats),
        'year_distribution': dict(sorted(year_stats.items())),
        'language_distribution': dict(language_stats),
        'date_range': {
            'earliest': min((p.get('created_at', '9999') for p in all_posts), default=''),
            'latest': max((p.get('created_at', '') for p in all_posts), default='')
        }
    }

    # 保存数据
    print("\n保存处理后的数据...")

    posts_path = processed_dir / "merged_posts.json"
    with open(posts_path, 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 帖子数据: {posts_path}")

    comments_path = processed_dir / "all_comments.json"
    with open(comments_path, 'w', encoding='utf-8') as f:
        json.dump(all_comments, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 评论数据: {comments_path}")

    stats_path = processed_dir / "data_statistics.json"
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(statistics, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 统计信息: {stats_path}")

    # 打印统计摘要
    print("\n" + "=" * 60)
    print("📊 数据统计摘要")
    print("=" * 60)

    print(f"\n📌 总体数据:")
    print(f"   - 总帖子数: {statistics['total_posts']}")
    print(f"   - 总评论数: {statistics['total_comments']}")
    print(f"   - 平均每帖评论数: {statistics['avg_comments_per_post']}")

    print(f"\n📌 平台分布:")
    for platform, stats in platform_stats.items():
        avg = round(stats['comments'] / stats['posts'], 1) if stats['posts'] > 0 else 0
        print(f"   - {platform.upper()}: {stats['posts']} 帖子, {stats['comments']} 评论 (平均 {avg})")

    print(f"\n📌 语言分布:")
    for lang, count in language_stats.items():
        lang_name = "英文" if lang == "en" else "中文" if lang == "zh" else lang
        print(f"   - {lang_name}: {count} 条")

    print(f"\n📌 时间范围:")
    print(f"   - 最早: {statistics['date_range']['earliest']}")
    print(f"   - 最晚: {statistics['date_range']['latest']}")

    print(f"\n📌 年份分布:")
    for year, count in sorted(year_stats.items()):
        print(f"   - {year}: {count} 帖子")

    print("\n" + "=" * 60)
    print("✅ 数据合并与清洗完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
