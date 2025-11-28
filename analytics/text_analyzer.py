"""
文本分析模块 - 简化版

提供基础的文本分析功能，如关键词提取、词频统计等
"""
from typing import List, Dict, Tuple
from collections import Counter
import re
import sys
import os
from loguru import logger

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config import KEYWORDS


class TextAnalyzer:
    """文本分析器"""

    def __init__(self):
        self.stop_words = self._load_stop_words()

    def _load_stop_words(self) -> set:
        """加载停用词（简化版）"""
        # 简单的中文停用词列表
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
            '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '为',
            '能', '这个', '那个', '什么', '可以', '吗', '吧', '啊', '呢'
        }
        return stop_words

    def analyze_texts(self, posts: List[Dict]) -> Dict:
        """
        分析帖子文本

        Args:
            posts: 帖子列表

        Returns:
            分析结果
        """
        logger.info(f"开始文本分析，共 {len(posts)} 条帖子")

        # 收集所有文本
        all_texts = []
        for post in posts:
            all_texts.append(post.get('title', ''))
            all_texts.append(post.get('content', ''))
            for comment in post.get('comments', []):
                all_texts.append(comment.get('content', ''))

        full_text = ' '.join(all_texts)

        return {
            'keyword_frequency': self._analyze_keyword_frequency(full_text),
            'word_frequency': self._analyze_word_frequency(full_text, top_n=30),
            'sentiment_distribution': self._analyze_sentiment_simple(posts),
        }

    def _analyze_keyword_frequency(self, text: str) -> Dict:
        """分析关键词频率"""
        text_lower = text.lower()

        frequencies = {}
        for category, keywords in KEYWORDS.items():
            if category == 'exclude':
                continue

            cat_freq = {}
            for keyword in keywords:
                count = text_lower.count(keyword.lower())
                if count > 0:
                    cat_freq[keyword] = count

            frequencies[category] = cat_freq

        return frequencies

    def _analyze_word_frequency(self, text: str, top_n: int = 30) -> List[Tuple[str, int]]:
        """
        分析词频（简单的基于空格分词）

        Args:
            text: 文本
            top_n: 返回前N个高频词

        Returns:
            词频列表
        """
        # 简单的中文分词（实际应该用jieba等工具）
        # 这里只做简单的字符级统计
        words = []

        # 提取中文词（2-4字）
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
        words.extend(chinese_words)

        # 提取英文词
        english_words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        words.extend(english_words)

        # 过滤停用词
        words = [w for w in words if w not in self.stop_words]

        # 统计词频
        word_counts = Counter(words)

        return word_counts.most_common(top_n)

    def _analyze_sentiment_simple(self, posts: List[Dict]) -> Dict:
        """
        简单的情感分析（基于关键词）

        Args:
            posts: 帖子列表

        Returns:
            情感分布
        """
        positive_keywords = ['机会', '学习', '成长', '提升', '优化', '创新', '未来', '帮助', '提高', '进步']
        negative_keywords = ['失业', '淘汰', '取代', '担心', '焦虑', '困难', '危机', '威胁', '消失', '裁员']

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for post in posts:
            text = (post.get('title', '') + ' ' + post.get('content', '')).lower()

            pos_matches = sum(1 for kw in positive_keywords if kw in text)
            neg_matches = sum(1 for kw in negative_keywords if kw in text)

            if pos_matches > neg_matches:
                positive_count += 1
            elif neg_matches > pos_matches:
                negative_count += 1
            else:
                neutral_count += 1

        total = len(posts)
        return {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count,
            'positive_percentage': positive_count / total * 100 if total > 0 else 0,
            'negative_percentage': negative_count / total * 100 if total > 0 else 0,
            'neutral_percentage': neutral_count / total * 100 if total > 0 else 0,
        }
