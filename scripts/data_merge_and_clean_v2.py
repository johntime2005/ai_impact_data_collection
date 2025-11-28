"""
数据合并与清洗脚本 v2
功能：合并Reddit和V2EX数据，进行清洗和标准化处理
使用更健壮的JSON解析方式
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(r"C:\Users\johntimeson\Desktop\ai_impact_data_collection")
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

    # 去除首尾空白
    text = text.strip()

    return text


def normalize_date(date_str: str) -> str:
    """标准化日期格式为 YYYY-MM-DD"""
    if not date_str:
        return ""

    # 处理相对时间（如 "7天前"）
    if "天前" in str(date_str):
        try:
            days = int(re.search(r'(\d+)', str(date_str)).group(1))
            date = datetime.now() - timedelta(days=days)
            return date.strftime("%Y-%m-%d")
        except:
            pass

    # 处理 "days ago" 格式
    if "days ago" in str(date_str).lower() or "day ago" in str(date_str).lower():
        try:
            days = int(re.search(r'(\d+)', str(date_str)).group(1))
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
            dt = datetime.strptime(str(date_str)[:26], fmt)
            return dt.strftime("%Y-%m-%d")
        except:
            continue

    # 尝试提取日期部分
    match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', str(date_str))
    if match:
        return match.group(1).replace('/', '-')

    return str(date_str)[:10] if date_str else ""


def safe_load_json(file_path: Path) -> dict | list | None:
    """安全加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 尝试修复常见JSON问题
            # 替换可能导致问题的特殊字符
            content = content.replace('\r\n', '\n')
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"  JSON解析错误: {e}")
        # 尝试更宽松的解析
        try:
            import ast
            with open(file_path, 'r', encoding='utf-8') as f:
                return ast.literal_eval(f.read())
        except:
            pass
    except Exception as e:
        print(f"  读取错误: {e}")
    return None


def load_reddit_posts() -> list:
    """加载Reddit帖子数据"""
    posts = []

    for i in range(1, 11):
        file_path = DATA_RAW_DIR / f"reddit_post_{i}.json"
        if file_path.exists():
            print(f"  处理 reddit_post_{i}.json...")
            post = safe_load_json(file_path)
            if post:
                posts.append(post)
                print(f"    ✓ 成功: {post.get('title', 'N/A')[:50]}...")
            else:
                print(f"    ✗ 失败")

    return posts


def load_v2ex_posts() -> list:
    """加载V2EX帖子数据"""
    file_path = DATA_RAW_DIR / "v2ex_ai_impact_posts.json"

    if file_path.exists():
        posts = safe_load_json(file_path)
        if posts:
            print(f"  ✓ V2EX帖子: {len(posts)} 个")
            return posts
        else:
            print(f"  ✗ V2EX加载失败")

    return []


def standardize_reddit_post(post: dict) -> dict:
    """标准化Reddit帖子格式"""
    comments = post.get('comments', [])

    standardized_comments = []
    for c in comments:
        if isinstance(c, dict):
            standardized_comments.append({
                "author": str(c.get('author', 'unknown')),
                "content": clean_text(str(c.get('content', ''))),
                "upvotes": int(c.get('upvotes', 0)) if c.get('upvotes') else 0,
                "created_at": normalize_date(c.get('created_at', '')),
            })

    url = post.get('url', '')
    post_id = url.split('/')[-2] if url and '/' in url else 'unknown'

    return {
        "id": f"reddit_{post_id}",
        "platform": "reddit",
        "subreddit": post.get('subreddit', ''),
        "url": url,
        "title": clean_text(str(post.get('title', ''))),
        "content": clean_text(str(post.get('content', ''))),
        "author": str(post.get('author', 'unknown')),
        "created_at": normalize_date(post.get('created_at', '')),
        "upvotes": int(post.get('upvotes', 0)) if post.get('upvotes') else 0,
        "comment_count": int(post.get('comment_count', len(comments))),
        "comments": standardized_comments,
        "language": "en",
        "scraped_at": str(post.get('scraped_at', '')),
    }


def standardize_v2ex_post(post: dict) -> dict:
    """标准化V2EX帖子格式"""
    comments = post.get('comments', [])

    standardized_comments = []
    for c in comments:
        if isinstance(c, dict):
            upvotes = c.get('upvotes', 0)
            if not isinstance(upvotes, int):
                upvotes = 0
            standardized_comments.append({
                "author": str(c.get('author', 'unknown')),
                "content": clean_text(str(c.get('content', ''))),
                "upvotes": upvotes,
                "created_at": normalize_date(c.get('created_at', c.get('time', ''))),
                "floor": c.get('floor', 0),
            })

    view_count = post.get('view_count', 0)
    if isinstance(view_count, str):
        # 处理 "7480" 或 "7480 次点击" 格式
        match = re.search(r'(\d+)', view_count)
        view_count = int(match.group(1)) if match else 0

    return {
        "id": f"v2ex_{post.get('topic_id', 'unknown')}",
        "platform": "v2ex",
        "url": post.get('url', ''),
        "title": clean_text(str(post.get('title', ''))),
        "content": clean_text(str(post.get('content', ''))),
        "author": str(post.get('author', 'unknown')),
        "created_at": normalize_date(post.get('created_at', '')),
        "view_count": view_count,
        "comment_count": int(post.get('comment_count', len(comments))),
        "comments": standardized_comments,
        "tags": post.get('tags', []),
        "language": "zh",
        "scraped_at": str(post.get('scraped_at', '')),
    }


def extract_all_comments(posts: list) -> list:
    """提取所有评论为独立列表"""
    all_comments = []

    for post in posts:
        post_id = post.get('id', '')
        platform = post.get('platform', '')
        post_title = post.get('title', '')
        post_date = post.get('created_at', '')

        for idx, comment in enumerate(post.get('comments', [])):
            all_comments.append({
                "comment_id": f"{post_id}_c{idx}",
                "post_id": post_id,
                "platform": platform,
                "post_title": post_title[:80] if post_title else '',
                "post_date": post_date,
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
        year = str(p.get('created_at', ''))[:4]
        if year and year.isdigit():
            year_dist[year] = year_dist.get(year, 0) + 1

    # 按平台统计评论数
    platform_comment_stats = {}
    for p in posts:
        platform = p['platform']
        if platform not in platform_comment_stats:
            platform_comment_stats[platform] = []
        platform_comment_stats[platform].append(p['comment_count'])

    stats = {
        "generated_at": datetime.now().isoformat(),
        "data_summary": {
            "total_posts": len(posts),
            "total_comments": len(comments),
            "avg_comments_per_post": round(len(comments) / len(posts), 1) if posts else 0,
        },
        "platform_distribution": {
            "reddit": {
                "posts": len(reddit_posts),
                "comments": len(reddit_comments),
                "avg_comments": round(len(reddit_comments) / len(reddit_posts), 1) if reddit_posts else 0,
            },
            "v2ex": {
                "posts": len(v2ex_posts),
                "comments": len(v2ex_comments),
                "avg_comments": round(len(v2ex_comments) / len(v2ex_posts), 1) if v2ex_posts else 0,
            }
        },
        "language_distribution": {
            "english": len(reddit_comments),
            "chinese": len(v2ex_comments),
        },
        "year_distribution": dict(sorted(year_dist.items())),
        "time_range": {
            "earliest": min([p.get('created_at', '9999') for p in posts if p.get('created_at')]),
            "latest": max([p.get('created_at', '0000') for p in posts if p.get('created_at')]),
        }
    }

    return stats


def main():
    """主函数"""
    print("=" * 60)
    print("数据合并与清洗 v2")
    print("=" * 60)

    # 1. 加载数据
    print("\n[1/4] 加载原始数据...")
    reddit_posts = load_reddit_posts()
    v2ex_posts = load_v2ex_posts()

    print(f"\n  加载结果: Reddit {len(reddit_posts)} 个, V2EX {len(v2ex_posts)} 个")

    # 2. 标准化数据
    print("\n[2/4] 标准化数据格式...")
    all_posts = []

    for post in reddit_posts:
        try:
            standardized = standardize_reddit_post(post)
            all_posts.append(standardized)
        except Exception as e:
            print(f"  ✗ Reddit帖子标准化失败: {e}")

    for post in v2ex_posts:
        try:
            standardized = standardize_v2ex_post(post)
            all_posts.append(standardized)
        except Exception as e:
            print(f"  ✗ V2EX帖子标准化失败: {e}")

    print(f"  ✓ 标准化完成: {len(all_posts)} 个帖子")

    # 3. 提取评论
    print("\n[3/4] 提取评论数据...")
    all_comments = extract_all_comments(all_posts)
    print(f"  ✓ 提取完成: {len(all_comments)} 条评论")

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
    print("📊 数据统计摘要")
    print("=" * 60)

    summary = stats['data_summary']
    print(f"\n📌 总体数据:")
    print(f"   - 总帖子数: {summary['total_posts']}")
    print(f"   - 总评论数: {summary['total_comments']}")
    print(f"   - 平均每帖评论数: {summary['avg_comments_per_post']}")

    print(f"\n📌 平台分布:")
    for platform, data in stats['platform_distribution'].items():
        print(f"   - {platform.upper()}: {data['posts']} 帖子, {data['comments']} 评论 (平均 {data['avg_comments']})")

    print(f"\n📌 语言分布:")
    lang = stats['language_distribution']
    print(f"   - 英文: {lang['english']} 条")
    print(f"   - 中文: {lang['chinese']} 条")

    print(f"\n📌 时间范围:")
    time_range = stats['time_range']
    print(f"   - 最早: {time_range['earliest']}")
    print(f"   - 最晚: {time_range['latest']}")

    print(f"\n📌 年份分布:")
    for year, count in stats['year_distribution'].items():
        print(f"   - {year}: {count} 帖子")

    print("\n" + "=" * 60)
    print("✅ 数据合并与清洗完成!")
    print("=" * 60)

    return all_posts, all_comments, stats


if __name__ == "__main__":
    main()
