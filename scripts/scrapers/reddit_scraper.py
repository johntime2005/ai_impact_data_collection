"""
Reddit数据采集脚本 - 使用公开JSON接口

使用Reddit的公开JSON API采集AI对程序员就业影响的讨论
无需API认证，完全免费！

使用方法:
直接运行: pixi run python reddit_scraper.py
"""

import requests
import time
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger
from urllib.parse import quote


class RedditJSONScraper:
    """Reddit公开JSON接口采集器"""

    def __init__(self):
        """初始化采集器"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.base_delay = 2  # 每个请求间隔2秒，避免被限制
        logger.info("✅ Reddit JSON采集器初始化成功")

    def search_subreddit(
        self,
        subreddit: str,
        query: str,
        min_comments: int = 100,
        limit: int = 100
    ) -> List[Dict]:
        """
        在指定subreddit搜索帖子

        Args:
            subreddit: subreddit名称（如"programming"）
            query: 搜索关键词
            min_comments: 最少评论数
            limit: 搜索结果数量限制

        Returns:
            符合条件的帖子列表（仅基本信息，不含评论）
        """
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            'q': query,
            'restrict_sr': 'on',  # 限制在当前subreddit
            'sort': 'comments',   # 按评论数排序
            't': 'all',           # 所有时间
            'limit': limit
        }

        try:
            logger.info(f"🔍 搜索 r/{subreddit} - 关键词: {query}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            posts = []

            for child in data['data']['children']:
                post = child['data']

                # 过滤：评论数要够
                if post['num_comments'] < min_comments:
                    continue

                # 过滤：不要被删除的帖子
                if post.get('removed_by_category') or post.get('removed'):
                    continue

                # 保存基本信息
                posts.append({
                    'id': post['id'],
                    'subreddit': post['subreddit'],
                    'title': post['title'],
                    'selftext': post.get('selftext', ''),
                    'author': post.get('author', '[deleted]'),
                    'created_utc': post['created_utc'],
                    'score': post['score'],
                    'upvote_ratio': post.get('upvote_ratio', 0),
                    'num_comments': post['num_comments'],
                    'permalink': post['permalink'],
                    'url': f"https://reddit.com{post['permalink']}"
                })

            logger.info(f"  ✅ 找到 {len(posts)} 个符合条件的帖子")
            time.sleep(self.base_delay)  # 延迟避免被限制
            return posts

        except Exception as e:
            logger.error(f"❌ 搜索失败: {e}")
            return []

    def get_post_with_comments(self, subreddit: str, post_id: str, max_comments: int = 100) -> Optional[Dict]:
        """
        获取帖子详情和评论

        Args:
            subreddit: subreddit名称
            post_id: 帖子ID
            max_comments: 最多提取评论数

        Returns:
            完整的帖子数据（包含评论）
        """
        url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/.json"

        try:
            logger.info(f"  📥 获取帖子 {post_id} 的评论...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            # 第一个元素是帖子信息
            post_data = data[0]['data']['children'][0]['data']

            # 第二个元素是评论列表
            comments_data = data[1]['data']['children']

            # 提取帖子基本信息
            post = {
                'platform': 'reddit',
                'type': 'submission',
                'url': f"https://reddit.com{post_data['permalink']}",
                'subreddit': post_data['subreddit'],
                'scraped_at': datetime.now().isoformat(),
                'title': post_data['title'],
                'content': post_data.get('selftext', '[链接帖子]'),
                'author': post_data.get('author', '[deleted]'),
                'created_at': datetime.fromtimestamp(post_data['created_utc']).isoformat(),
                'upvotes': post_data['score'],
                'upvote_ratio': post_data.get('upvote_ratio', 0),
                'comment_count': post_data['num_comments'],
                'comments': []
            }

            # 提取评论
            comment_count = 0
            for comment_obj in comments_data:
                if comment_count >= max_comments:
                    break

                # 跳过"更多评论"占位符
                if comment_obj['kind'] == 'more':
                    continue

                comment = comment_obj['data']

                # 跳过被删除的评论
                if comment.get('author') == '[deleted]' and comment.get('body') == '[deleted]':
                    continue

                post['comments'].append({
                    'author': comment.get('author', '[deleted]'),
                    'content': comment.get('body', ''),
                    'created_at': datetime.fromtimestamp(comment['created_utc']).isoformat(),
                    'upvotes': comment['score'],
                })

                comment_count += 1

            logger.info(f"    ✅ 提取了 {comment_count} 条评论")

            # 添加相关性标记
            post['is_relevant'] = True
            post['relevance_note'] = 'Reddit公开API采集 - AI对程序员影响相关讨论'

            time.sleep(self.base_delay)  # 延迟避免被限制
            return post

        except Exception as e:
            logger.error(f"❌ 获取帖子失败: {e}")
            return None

    def collect_posts(
        self,
        subreddits: List[str],
        keywords: List[str],
        min_comments: int = 100,
        target_count: int = 10
    ) -> List[Dict]:
        """
        采集Reddit帖子

        Args:
            subreddits: 要搜索的subreddit列表
            keywords: 关键词列表
            min_comments: 最少评论数
            target_count: 目标采集数量

        Returns:
            完整的帖子列表（包含评论）
        """
        all_posts = []
        collected_ids = set()

        for subreddit in subreddits:
            if len(all_posts) >= target_count:
                break

            for keyword in keywords:
                if len(all_posts) >= target_count:
                    break

                # 搜索帖子（仅基本信息）
                basic_posts = self.search_subreddit(
                    subreddit=subreddit,
                    query=keyword,
                    min_comments=min_comments,
                    limit=50
                )

                # 获取每个帖子的完整数据（包括评论）
                for basic_post in basic_posts:
                    if len(all_posts) >= target_count:
                        break

                    # 去重
                    if basic_post['id'] in collected_ids:
                        continue

                    # 获取完整数据
                    full_post = self.get_post_with_comments(
                        subreddit=basic_post['subreddit'],
                        post_id=basic_post['id'],
                        max_comments=100
                    )

                    if full_post:
                        all_posts.append(full_post)
                        collected_ids.add(basic_post['id'])
                        logger.info(f"✅ 已采集 {len(all_posts)}/{target_count} 个帖子")

        return all_posts

    def save_posts(self, posts: List[Dict], output_file: str):
        """
        保存帖子数据到JSON文件

        Args:
            posts: 帖子列表
            output_file: 输出文件路径
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)

        logger.info(f"💾 数据已保存到: {output_path}")
        logger.info(f"📊 共保存 {len(posts)} 个帖子")


def main():
    """主函数"""
    logger.info("🚀 开始Reddit数据采集...")

    # 初始化采集器
    scraper = RedditJSONScraper()

    # 目标subreddit
    subreddits = [
        'programming',           # 编程讨论
        'cscareerquestions',     # CS职业问题
        'artificial',            # AI讨论
        'MachineLearning',       # 机器学习
        'learnprogramming',      # 编程学习
        'Python',                # Python相关
        'javascript',            # JavaScript相关
    ]

    # 搜索关键词
    keywords = [
        'ChatGPT programmer job',
        'AI replace developers',
        'GPT impact software engineer',
        'artificial intelligence programming career',
        'ChatGPT coding job market',
    ]

    # 采集帖子
    posts = scraper.collect_posts(
        subreddits=subreddits,
        keywords=keywords,
        min_comments=100,  # 最少100条评论
        target_count=15    # 目标15个帖子（留点余量）
    )

    logger.info(f"📊 采集完成！共获取 {len(posts)} 个帖子")

    # 保存结果
    if posts:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/raw/reddit_posts_{timestamp}.json"
        scraper.save_posts(posts, output_file)

        # 统计信息
        total_comments = sum(len(post['comments']) for post in posts)
        avg_comments = total_comments / len(posts) if posts else 0

        logger.info("📊 统计信息:")
        logger.info(f"  帖子数量: {len(posts)}")
        logger.info(f"  总评论数: {total_comments}")
        logger.info(f"  平均每帖评论数: {avg_comments:.1f}")

        # 显示subreddit分布
        subreddit_counts = {}
        for post in posts:
            sr = post['subreddit']
            subreddit_counts[sr] = subreddit_counts.get(sr, 0) + 1

        logger.info("  Subreddit分布:")
        for sr, count in sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"    r/{sr}: {count} 个帖子")

    else:
        logger.warning("⚠️ 没有采集到任何数据")

    logger.info("✅ Reddit数据采集完成！")


if __name__ == "__main__":
    main()
