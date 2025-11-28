"""
辅助函数模块 - 各种通用工具函数
"""
import re
from datetime import datetime, timedelta
from typing import Optional, List, Set
from dateutil import parser as date_parser


def parse_relative_time(time_text: str, reference_time: Optional[datetime] = None) -> Optional[datetime]:
    """
    解析相对时间文本（如"2小时前"、"3天前"）

    Args:
        time_text: 时间文本
        reference_time: 参考时间，默认为当前时间

    Returns:
        解析后的datetime对象，失败返回None
    """
    if not time_text:
        return None

    if reference_time is None:
        reference_time = datetime.now()

    time_text = time_text.strip()

    # 匹配模式
    patterns = [
        (r'(\d+)\s*秒前', 'seconds'),
        (r'(\d+)\s*分钟前', 'minutes'),
        (r'(\d+)\s*小时前', 'hours'),
        (r'(\d+)\s*天前', 'days'),
        (r'(\d+)\s*周前', 'weeks'),
        (r'(\d+)\s*月前', 'months'),
        (r'(\d+)\s*年前', 'years'),
    ]

    for pattern, unit in patterns:
        match = re.search(pattern, time_text)
        if match:
            value = int(match.group(1))

            if unit == 'seconds':
                delta = timedelta(seconds=value)
            elif unit == 'minutes':
                delta = timedelta(minutes=value)
            elif unit == 'hours':
                delta = timedelta(hours=value)
            elif unit == 'days':
                delta = timedelta(days=value)
            elif unit == 'weeks':
                delta = timedelta(weeks=value)
            elif unit == 'months':
                delta = timedelta(days=value * 30)  # 近似
            elif unit == 'years':
                delta = timedelta(days=value * 365)  # 近似
            else:
                continue

            return reference_time - delta

    # 尝试解析为标准日期格式
    try:
        return date_parser.parse(time_text, fuzzy=True)
    except Exception:
        pass

    return None


def clean_text(text: str, remove_newlines: bool = False) -> str:
    """
    清理文本内容

    Args:
        text: 原始文本
        remove_newlines: 是否移除换行符

    Returns:
        清理后的文本
    """
    if not text:
        return ""

    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)

    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)

    # 移除换行符（可选）
    if remove_newlines:
        text = text.replace('\n', ' ').replace('\r', '')

    # 去除首尾空白
    text = text.strip()

    return text


def extract_keywords(
    text: str,
    keyword_sets: dict[str, List[str]],
    case_sensitive: bool = False
) -> dict[str, List[str]]:
    """
    从文本中提取关键词

    Args:
        text: 要分析的文本
        keyword_sets: 关键词集合，格式：{"类别": ["关键词1", "关键词2"]}
        case_sensitive: 是否大小写敏感

    Returns:
        找到的关键词，格式：{"类别": ["找到的关键词1", "找到的关键词2"]}
    """
    if not text:
        return {key: [] for key in keyword_sets}

    if not case_sensitive:
        text = text.lower()

    results = {}

    for category, keywords in keyword_sets.items():
        found = []
        for keyword in keywords:
            search_keyword = keyword if case_sensitive else keyword.lower()
            if search_keyword in text:
                found.append(keyword)
        results[category] = found

    return results


def calculate_relevance_score(
    text: str,
    primary_keywords: List[str],
    secondary_keywords: List[str],
    exclude_keywords: Optional[List[str]] = None
) -> float:
    """
    计算文本相关性得分

    Args:
        text: 要分析的文本
        primary_keywords: 主关键词列表
        secondary_keywords: 次关键词列表
        exclude_keywords: 排除关键词列表

    Returns:
        相关性得分 (0.0-1.0)
    """
    if not text:
        return 0.0

    text_lower = text.lower()
    score = 0.0

    # 检查排除关键词
    if exclude_keywords:
        for keyword in exclude_keywords:
            if keyword.lower() in text_lower:
                return 0.0  # 包含排除关键词，直接返回0

    # 主关键词匹配（权重0.6）
    primary_matches = sum(1 for kw in primary_keywords if kw.lower() in text_lower)
    if primary_matches > 0:
        score += min(primary_matches / len(primary_keywords), 1.0) * 0.6

    # 次关键词匹配（权重0.4）
    secondary_matches = sum(1 for kw in secondary_keywords if kw.lower() in text_lower)
    if secondary_matches > 0:
        score += min(secondary_matches / len(secondary_keywords), 1.0) * 0.4

    return min(score, 1.0)


def format_count(count: int) -> str:
    """
    格式化计数（如1234 -> 1.2K, 1234567 -> 1.2M）

    Args:
        count: 数字

    Returns:
        格式化后的字符串
    """
    if count < 1000:
        return str(count)
    elif count < 1000000:
        return f"{count / 1000:.1f}K"
    elif count < 1000000000:
        return f"{count / 1000000:.1f}M"
    else:
        return f"{count / 1000000000:.1f}B"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本

    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀

    Returns:
        截断后的文本
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix
