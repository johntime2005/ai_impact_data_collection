"""
数据质量分析模块

用于评估采集数据的质量，生成质量报告
"""
from typing import List, Dict
from datetime import datetime
from collections import Counter
import sys
import os
from loguru import logger

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config import MIN_COMMENTS_PER_POST, MIN_POSTS_REQUIRED, TIME_PERIODS, KEYWORDS


class QualityAnalyzer:
    """数据质量分析器"""

    def __init__(self):
        self.analysis_result = {}

    def analyze(self, posts: List[Dict]) -> Dict:
        """
        执行完整的质量分析

        Args:
            posts: 帖子列表

        Returns:
            分析结果字典
        """
        logger.info(f"开始质量分析，共 {len(posts)} 条帖子")

        self.analysis_result = {
            'basic_stats': self._analyze_basic_stats(posts),
            'platform_distribution': self._analyze_platform_distribution(posts),
            'time_distribution': self._analyze_time_distribution(posts),
            'comment_stats': self._analyze_comment_stats(posts),
            'quality_checks': self._perform_quality_checks(posts),
            'keyword_coverage': self._analyze_keyword_coverage(posts),
        }

        return self.analysis_result

    def _analyze_basic_stats(self, posts: List[Dict]) -> Dict:
        """基础统计"""
        total_posts = len(posts)
        total_comments = sum(len(post.get('comments', [])) for post in posts)

        valid_posts = [
            post for post in posts
            if len(post.get('comments', [])) >= MIN_COMMENTS_PER_POST
        ]

        return {
            'total_posts': total_posts,
            'valid_posts': len(valid_posts),
            'total_comments': total_comments,
            'avg_comments_per_post': total_comments / total_posts if total_posts > 0 else 0,
            'min_comments': min((len(post.get('comments', [])) for post in posts), default=0),
            'max_comments': max((len(post.get('comments', [])) for post in posts), default=0),
        }

    def _analyze_platform_distribution(self, posts: List[Dict]) -> Dict:
        """平台分布统计"""
        platform_counts = Counter(post.get('platform', 'unknown') for post in posts)

        return {
            'platforms': dict(platform_counts),
            'platform_percentages': {
                platform: count / len(posts) * 100
                for platform, count in platform_counts.items()
            } if posts else {}
        }

    def _analyze_time_distribution(self, posts: List[Dict]) -> Dict:
        """时间分布统计"""
        time_counts = {period['name']: 0 for period in TIME_PERIODS}

        for post in posts:
            created_at = post.get('created_at')
            if not created_at:
                continue

            # 尝试解析时间
            try:
                if isinstance(created_at, str):
                    # 简单处理，实际可能需要更复杂的解析
                    post_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                elif isinstance(created_at, datetime):
                    post_date = created_at
                else:
                    continue

                # 判断属于哪个时间段
                for period in TIME_PERIODS:
                    start = datetime.fromisoformat(period['start'])
                    end = datetime.fromisoformat(period['end'])
                    if start <= post_date <= end:
                        time_counts[period['name']] += 1
                        break

            except Exception as e:
                logger.debug(f"解析时间失败: {created_at} - {e}")
                continue

        return {
            'time_periods': time_counts,
            'total_with_time': sum(time_counts.values()),
            'without_time': len(posts) - sum(time_counts.values())
        }

    def _analyze_comment_stats(self, posts: List[Dict]) -> Dict:
        """评论统计分析"""
        all_comments = []
        for post in posts:
            all_comments.extend(post.get('comments', []))

        if not all_comments:
            return {
                'total_comments': 0,
                'avg_length': 0,
                'high_quality_count': 0
            }

        # 评论长度统计
        comment_lengths = [len(c.get('content', '')) for c in all_comments]

        # 高质量评论（点赞数>10且长度>50）
        high_quality = [
            c for c in all_comments
            if c.get('upvotes', 0) > 10 and len(c.get('content', '')) > 50
        ]

        return {
            'total_comments': len(all_comments),
            'avg_length': sum(comment_lengths) / len(comment_lengths) if comment_lengths else 0,
            'min_length': min(comment_lengths) if comment_lengths else 0,
            'max_length': max(comment_lengths) if comment_lengths else 0,
            'high_quality_count': len(high_quality),
            'high_quality_percentage': len(high_quality) / len(all_comments) * 100 if all_comments else 0
        }

    def _perform_quality_checks(self, posts: List[Dict]) -> Dict:
        """执行质量检查"""
        checks = {
            'meets_min_posts': len(posts) >= MIN_POSTS_REQUIRED,
            'meets_min_comments': sum(1 for p in posts if len(p.get('comments', [])) >= MIN_COMMENTS_PER_POST) >= MIN_POSTS_REQUIRED,
            'has_time_info': sum(1 for p in posts if p.get('created_at')) / len(posts) * 100 if posts else 0,
            'has_author_info': sum(1 for p in posts if p.get('author')) / len(posts) * 100 if posts else 0,
            'avg_content_length': sum(len(p.get('content', '')) for p in posts) / len(posts) if posts else 0,
        }

        # 总体质量评分 (0-100)
        score = 0
        if checks['meets_min_posts']:
            score += 30
        if checks['meets_min_comments']:
            score += 30
        score += min(checks['has_time_info'] * 0.2, 20)
        score += min(checks['has_author_info'] * 0.2, 20)

        checks['overall_quality_score'] = round(score, 2)

        return checks

    def _analyze_keyword_coverage(self, posts: List[Dict]) -> Dict:
        """关键词覆盖分析"""
        from utils.helpers import extract_keywords

        primary_matches = {kw: 0 for kw in KEYWORDS['primary']}
        secondary_matches = {kw: 0 for kw in KEYWORDS['secondary']}

        for post in posts:
            # 合并标题和内容
            text = (post.get('title', '') + ' ' + post.get('content', '')).lower()

            # 统计关键词出现
            for kw in KEYWORDS['primary']:
                if kw.lower() in text:
                    primary_matches[kw] += 1

            for kw in KEYWORDS['secondary']:
                if kw.lower() in text:
                    secondary_matches[kw] += 1

        return {
            'primary_keyword_matches': primary_matches,
            'secondary_keyword_matches': secondary_matches,
            'posts_with_primary': sum(1 for v in primary_matches.values() if v > 0),
            'posts_with_secondary': sum(1 for v in secondary_matches.values() if v > 0),
        }

    def generate_summary(self) -> str:
        """生成分析摘要文本"""
        if not self.analysis_result:
            return "尚未执行分析"

        basic = self.analysis_result['basic_stats']
        quality = self.analysis_result['quality_checks']

        summary = f"""
=== 数据质量分析报告 ===

【基础统计】
- 总帖子数: {basic['total_posts']}
- 有效帖子数: {basic['valid_posts']} (评论≥{MIN_COMMENTS_PER_POST})
- 总评论数: {basic['total_comments']}
- 平均每帖评论数: {basic['avg_comments_per_post']:.1f}

【质量检查】
- 满足最少帖子数要求: {'✓' if quality['meets_min_posts'] else '✗'}
- 满足最少评论数要求: {'✓' if quality['meets_min_comments'] else '✗'}
- 包含时间信息: {quality['has_time_info']:.1f}%
- 包含作者信息: {quality['has_author_info']:.1f}%
- 总体质量评分: {quality['overall_quality_score']}/100

【建议】
"""

        if not quality['meets_min_posts']:
            summary += f"- ⚠️ 帖子数不足，当前{basic['total_posts']}，需要{MIN_POSTS_REQUIRED}\n"

        if not quality['meets_min_comments']:
            summary += f"- ⚠️ 有效帖子数不足，需要更多评论数≥{MIN_COMMENTS_PER_POST}的帖子\n"

        if quality['overall_quality_score'] >= 80:
            summary += "- ✓ 数据质量良好，可以进行分析\n"
        elif quality['overall_quality_score'] >= 60:
            summary += "- ⚠️ 数据质量中等，建议补充更多数据\n"
        else:
            summary += "- ✗ 数据质量较差，需要重新采集\n"

        return summary

    def get_result(self) -> Dict:
        """获取完整分析结果"""
        return self.analysis_result
