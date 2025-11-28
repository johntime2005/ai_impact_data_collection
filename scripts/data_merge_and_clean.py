"""
数据合并与清洗脚本
功能：合并Reddit和V2EX数据，进行清洗和标准化处理
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# 确保输出目录存在
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(text: str) -> str:
    """清洗文本内容"""
    if not text:
        return ""

    # 移除多余空白字符
    text = re.sub(r'\s+', ' ', text)

    # 移除特殊控制字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # 移除URL（保留文本可读性）
    # text = re.sub(r'https?://\S+', '[链接]', text)

    # 去除首尾空白
    text = text.strip()

    return text


def normalize_date(date_str: str) -> str:
    """标准化日期格式为 YYYY-MM-DD"""
    if not date_str:
        return ""

    # 处理相对时间（如 "7天前"）
    if "天前" in date_str:
        try:
            days = int(re.search(r'(\d+)', date_str).group(1))
            from datetime import timedelta
            date = datetime.now() - timedelta(days=days)
            return date.strftime("%Y-%m-%d")
        except:
            pass

    # 处理 "days ago" 格式
    if "days ago" in date_str.lower() or "day ago" in date_str.lower():
        try:
            days = int(re.search(r'(\d+)', date_str).group(1))
            from datetime import timedelta
            date = datetime.now() - timedelta(days=days)
            return date.strftime("%Y-%m-%d")
        except:
            pass

    # 尝试解析标准日期格式
    date_formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S %z",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str[:26], fmt)
            return dt.strftime("%Y-%m-%d")
        except:
            continue

    # 尝试提取日期部分
    match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', date_str)
    if match:
        return match.group(1).replace('/', '-')

    return date_str


def load_reddit_posts() -> list:
    """加载Reddit帖子数据"""
    posts = []

    for i in range(1, 11):
        file_path = DATA_RAW_DIR / f"reddit_post_{i}.json"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    post = json.load(f)
                    posts.append(post)
                    print(f"✓ 加载 Reddit 帖子 {i}: {post.get('title', 'N/A')[:50]}...")
            except Exception as e:
                print(f"✗ 加载 Reddit 帖子 {i} 失败: {e}")

    return posts


def load_v2ex_posts() -> list:
    """加载V2EX帖子数据"""
    file_path = DATA_RAW_DIR / "v2ex_ai_impact_posts.json"

    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                posts = json.load(f)
                print(f"✓ 加载 V2EX 帖子: {len(posts)} 个")
                return posts
        except Exception as e:
            print(f"✗ 加载 V2EX 数据失败: {e}")

    return []


def standardize_reddit_post(post: dict) -> dict:
    """标准化Reddit帖子格式"""
    comments = post.get('comments', [])

    standardized_comments = []
    for c in comments:
        standardized_comments.append({
            "author": c.get('author', 'unknown'),
            "content": clean_text(c.get('content', '')),
            "upvotes": c.get('upvotes', 0),
            "created_at": normalize_date(c.get('created_at', '')),
        })

    return {
        "id": f"reddit_{post.get('url', '').split('/')[-2] if '/' in post.get('url', '') else 'unknown'}",
        "platform": "reddit",
        "subreddit": post.get('subreddit', ''),
        "url": post.get('url', ''),
        "title": clean_text(post.get('title', '')),
        "content": clean_text(post.get('content', '')),
        "author": post.get('author', 'unknown'),
        "created_at": normalize_date(post.get('created_at', '')),
        "upvotes": post.get('upvotes', 0),
        "comment_count": post.get('comment_count', len(comments)),
        "comments": standardized_comments,
        "language": "en",
        "scraped_at": post.get('scraped_at', ''),
    }


def standardize_v2ex_post(post: dict) -> dict:
    """标准化V2EX帖子格式"""
    comments = post.get('comments', [])

    standardized_comments = []
    for c in comments:
        standardized_comments.append({
            "author": c.get('author', 'unknown'),
            "content": clean_text(c.get('content', '')),
            "upvotes": c.get('upvotes', 0) if isinstance(c.get('upvotes'), int) else 0,
            "created_at": normalize_date(c.get('created_at', c.get('time', ''))),
            "floor": c.get('floor', 0),
        })

    return {
        "id": f"v2ex_{post.get('topic_id', 'unknown')}",
        "platform": "v2ex",
        "url": post.get('url', ''),
        "title": clean_text(post.get('title', '')),
        "content": clean_text(post.get('content', '')),
        "author": post.get('author', 'unknown'),
        "created_at": normalize_date(post.get('created_at', '')),
        "view_count": post.get('view_count', 0),
        "comment_count": post.get('comment_count', len(comments)),
        "comments": standardized_comments,
        "tags": post.get('tags', []),
        "language": "zh",
        "scraped_at": post.get('scraped_at', ''),
    }


def extract_all_comments(posts: list) -> list:
    """提取所有评论为独立列表"""
    all_comments = []

    for post in posts:
        post_id = post.get('id', '')
        platform = post.get('platform', '')
        post_title = post.get('title', '')

        for comment in post.get('comments', []):
            all_comments.append({
                "post_id": post_id,
                "platform": platform,
                "post_title": post_title[:50],
                "author": comment.get('author', ''),
                "content": comment.get('content', ''),
                "upvotes": comment.get('upvotes', 0),
                "created_at": comment.get('created_at', ''),
                "language": post.get('language', ''),
            })

    return all_comments


def generate_statistics(posts: list, comments: list) -> dict:
    """生成数据统计信息"""
    reddit_posts = [p for p in posts if p['platform'] == 'reddit']
    v2ex_posts = [p for p in posts if p['platform'] == 'v2ex']

    reddit_comments = [c for c in comments if c['platform'] == 'reddit']
    v2ex_comments = [c for c in comments if c['platform'] == 'v2ex']

    # 按年份统计
    year_dist = {}
    for p in posts:
        year = p.get('created_at', '')[:4]
        if year:
            year_dist[year] = year_dist.get(year, 0) + 1

    stats = {
        "generated_at": datetime.now().isoformat(),
        "总帖子数": len(posts),
        "总评论数": len(comments),
        "平台分布": {
            "Reddit": {
                "帖子数": len(reddit_posts),
                "评论数": len(reddit_comments),
            },
            "V2EX": {
                "帖子数": len(v2ex_posts),
                "评论数": len(v2ex_comments),
            }
        },
        "语言分布": {
            "英文": len(reddit_comments),
            "中文": len(v2ex_comments),
        },
        "年份分布": year_dist,
        "平均每帖评论数": round(len(comments) / len(posts), 1) if posts else 0,
    }

    return stats


def main():
    """主函数"""
    print("=" * 60)
    print("数据合并与清洗")
    print("=" * 60)

    # 1. 加载数据
    print("\n[1/4] 加载原始数据...")
    reddit_posts = load_reddit_posts()
    v2ex_posts = load_v2ex_posts()

    # 2. 标准化数据
    print("\n[2/4] 标准化数据格式...")
    all_posts = []

    for post in reddit_posts:
        standardized = standardize_reddit_post(post)
        all_posts.append(standardized)

    for post in v2ex_posts:
        standardized = standardize_v2ex_post(post)
        all_posts.append(standardized)

    print(f"  - 标准化完成: {len(all_posts)} 个帖子")

    # 3. 提取评论
    print("\n[3/4] 提取评论数据...")
    all_comments = extract_all_comments(all_posts)
    print(f"  - 提取完成: {len(all_comments)} 条评论")

    # 4. 生成统计
    print("\n[4/4] 生成统计信息...")
    stats = generate_statistics(all_posts, all_comments)

    # 保存结果
    print("\n保存处理后的数据...")

    # 保存合并后的帖子数据
    posts_output = DATA_PROCESSED_DIR / "merged_posts.json"
    with open(posts_output, 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 帖子数据: {posts_output}")

    # 保存评论数据
    comments_output = DATA_PROCESSED_DIR / "all_comments.json"
    with open(comments_output, 'w', encoding='utf-8') as f:
        json.dump(all_comments, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 评论数据: {comments_output}")

    # 保存统计信息
    stats_output = DATA_PROCESSED_DIR / "data_statistics.json"
    with open(stats_output, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 统计信息: {stats_output}")

    # 打印统计摘要
    print("\n" + "=" * 60)
    print("数据统计摘要")
    print("=" * 60)
    print(f"总帖子数: {stats['总帖子数']}")
    print(f"总评论数: {stats['总评论数']}")
    print(f"平均每帖评论数: {stats['平均每帖评论数']}")
    print(f"\n平台分布:")
    for platform, data in stats['平台分布'].items():
        print(f"  - {platform}: {data['帖子数']} 帖子, {data['评论数']} 评论")
    print(f"\n年份分布:")
    for year, count in sorted(stats['年份分布'].items()):
        print(f"  - {year}: {count} 帖子")

    print("\n✅ 数据合并与清洗完成!")

    return all_posts, all_comments, stats


if __name__ == "__main__":
    main()
