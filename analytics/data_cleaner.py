"""
数据清洗模块 - 使用Polars进行高性能数据处理
"""
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    logger.warning("Polars未安装，将使用基础Python处理")

from models.post import Post
from models.comment import Comment
from utils.helpers import clean_text


class DataCleaner:
    """数据清洗器"""

    def __init__(self):
        self.stats = {
            'total_posts': 0,
            'removed_duplicates': 0,
            'cleaned_comments': 0,
            'invalid_removed': 0
        }

    def clean_posts(self, posts: List[Dict]) -> List[Dict]:
        """
        清洗帖子数据

        Args:
            posts: 原始帖子列表

        Returns:
            清洗后的帖子列表
        """
        logger.info(f"开始清洗数据，共 {len(posts)} 条帖子")
        self.stats['total_posts'] = len(posts)

        if POLARS_AVAILABLE:
            return self._clean_with_polars(posts)
        else:
            return self._clean_with_python(posts)

    def _clean_with_polars(self, posts: List[Dict]) -> List[Dict]:
        """
        使用Polars进行高性能清洗

        Args:
            posts: 原始帖子列表

        Returns:
            清洗后的帖子列表
        """
        logger.info("使用Polars进行数据清洗（高性能模式）")

        # 转换为DataFrame（只处理基础字段，评论单独处理）
        basic_fields = []
        for post in posts:
            basic = {
                'url': post.get('url', ''),
                'platform': post.get('platform', ''),
                'title': post.get('title', ''),
                'content': post.get('content', ''),
                'author': post.get('author', ''),
                'created_at': post.get('created_at'),
            }
            basic_fields.append(basic)

        df = pl.DataFrame(basic_fields)

        # 1. 去重（基于URL）
        original_len = len(df)
        df = df.unique(subset=['url'], keep='first')
        self.stats['removed_duplicates'] = original_len - len(df)

        logger.info(f"去除重复帖子: {self.stats['removed_duplicates']} 条")

        # 2. 清洗文本字段
        df = df.with_columns([
            pl.col('title').map_elements(lambda x: clean_text(str(x)) if x else '').alias('title'),
            pl.col('content').map_elements(lambda x: clean_text(str(x)) if x else '').alias('content'),
        ])

        # 3. 过滤无效数据（标题或URL为空）
        original_len = len(df)
        df = df.filter(
            (pl.col('title').str.len_chars() > 0) &
            (pl.col('url').str.len_chars() > 0)
        )
        self.stats['invalid_removed'] = original_len - len(df)

        logger.info(f"移除无效帖子: {self.stats['invalid_removed']} 条")

        # 4. 转回字典列表，并处理评论
        cleaned_posts = []
        cleaned_urls = df['url'].to_list()

        for post in posts:
            if post.get('url') in cleaned_urls:
                # 清洗评论
                if 'comments' in post and post['comments']:
                    post['comments'] = self._clean_comments(post['comments'])
                    self.stats['cleaned_comments'] += len(post['comments'])

                cleaned_posts.append(post)

        logger.info(f"数据清洗完成，保留 {len(cleaned_posts)} 条帖子")
        return cleaned_posts

    def _clean_with_python(self, posts: List[Dict]) -> List[Dict]:
        """
        使用纯Python进行清洗（兼容模式）

        Args:
            posts: 原始帖子列表

        Returns:
            清洗后的帖子列表
        """
        logger.info("使用Python进行数据清洗（兼容模式）")

        # 1. 去重
        seen_urls = set()
        unique_posts = []

        for post in posts:
            url = post.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_posts.append(post)
            else:
                self.stats['removed_duplicates'] += 1

        logger.info(f"去除重复帖子: {self.stats['removed_duplicates']} 条")

        # 2. 清洗和过滤
        cleaned_posts = []

        for post in unique_posts:
            # 清洗文本字段
            if 'title' in post:
                post['title'] = clean_text(post['title'])
            if 'content' in post:
                post['content'] = clean_text(post['content'])

            # 验证必要字段
            if not post.get('title') or not post.get('url'):
                self.stats['invalid_removed'] += 1
                continue

            # 清洗评论
            if 'comments' in post and post['comments']:
                post['comments'] = self._clean_comments(post['comments'])
                self.stats['cleaned_comments'] += len(post['comments'])

            cleaned_posts.append(post)

        logger.info(f"移除无效帖子: {self.stats['invalid_removed']} 条")
        logger.info(f"数据清洗完成，保留 {len(cleaned_posts)} 条帖子")

        return cleaned_posts

    def _clean_comments(self, comments: List[Dict]) -> List[Dict]:
        """
        清洗评论列表

        Args:
            comments: 原始评论列表

        Returns:
            清洗后的评论列表
        """
        cleaned = []

        for comment in comments:
            # 清洗内容
            if 'content' in comment:
                comment['content'] = clean_text(comment['content'])

            # 过滤空评论
            if not comment.get('content'):
                continue

            # 确保数值字段为整数
            for field in ['upvotes', 'downvotes']:
                if field in comment:
                    try:
                        comment[field] = int(comment[field])
                    except (ValueError, TypeError):
                        comment[field] = 0

            cleaned.append(comment)

        return cleaned

    def get_stats(self) -> Dict:
        """获取清洗统计信息"""
        return self.stats

    def deduplicate_by_content_similarity(
        self,
        posts: List[Dict],
        similarity_threshold: float = 0.9
    ) -> List[Dict]:
        """
        基于内容相似度去重（可选的高级功能）

        Args:
            posts: 帖子列表
            similarity_threshold: 相似度阈值

        Returns:
            去重后的帖子列表
        """
        # 这个功能需要额外的NLP库，这里只提供框架
        logger.warning("内容相似度去重功能需要额外实现")
        return posts
