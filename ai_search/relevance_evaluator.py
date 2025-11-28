"""
相关性评估器 - 使用AI评估帖子与主题的相关性

可以减少人工判断工作量
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
import sys
import os
from loguru import logger

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config import KEYWORDS


@dataclass
class RelevanceScore:
    """相关性评分"""
    url: str
    score: float  # 0.0-1.0
    is_relevant: bool
    reasons: List[str]
    confidence: float  # 0.0-1.0


class RelevanceEvaluator:
    """相关性评估器"""

    def __init__(self):
        self.evaluation_criteria = {
            'primary_keywords': KEYWORDS['primary'],
            'secondary_keywords': KEYWORDS['secondary'],
            'exclude_keywords': KEYWORDS['exclude']
        }

    def evaluate_post_simple(self, post_data: Dict) -> RelevanceScore:
        """
        简单评估（基于关键词）

        Args:
            post_data: 帖子数据

        Returns:
            相关性评分
        """
        title = post_data.get('title', '').lower()
        content = post_data.get('content', '').lower()
        full_text = title + ' ' + content

        score = 0.0
        reasons = []

        # 检查排除关键词
        for exclude_kw in self.evaluation_criteria['exclude_keywords']:
            if exclude_kw.lower() in full_text:
                return RelevanceScore(
                    url=post_data.get('url', ''),
                    score=0.0,
                    is_relevant=False,
                    reasons=[f"包含排除关键词: {exclude_kw}"],
                    confidence=0.9
                )

        # 主关键词匹配
        primary_matches = []
        for kw in self.evaluation_criteria['primary_keywords']:
            if kw.lower() in full_text:
                primary_matches.append(kw)
                score += 0.4

        if primary_matches:
            reasons.append(f"匹配主关键词: {', '.join(primary_matches)}")

        # 次关键词匹配
        secondary_matches = []
        for kw in self.evaluation_criteria['secondary_keywords']:
            if kw.lower() in full_text:
                secondary_matches.append(kw)
                score += 0.1

        if secondary_matches:
            reasons.append(f"匹配次关键词: {', '.join(secondary_matches[:5])}")

        # 归一化得分
        score = min(score, 1.0)

        # 判断是否相关
        is_relevant = score >= 0.5

        if not reasons:
            reasons.append("未找到相关关键词")

        return RelevanceScore(
            url=post_data.get('url', ''),
            score=score,
            is_relevant=is_relevant,
            reasons=reasons,
            confidence=0.7  # 简单评估的置信度较低
        )

    def evaluate_post_ai_assisted(self, post_data: Dict) -> RelevanceScore:
        """
        AI辅助评估（需要调用LLM）

        这个方法会生成提示词，让AI助手判断相关性

        Args:
            post_data: 帖子数据

        Returns:
            相关性评分
        """
        prompt = self._generate_evaluation_prompt(post_data)

        logger.info("需要AI助手评估相关性:")
        logger.info(f"URL: {post_data.get('url')}")
        logger.info(f"标题: {post_data.get('title')}")

        # 这里返回提示词，实际评估由AI助手完成
        return {
            'needs_ai_evaluation': True,
            'prompt': prompt,
            'post_data': post_data
        }

    def _generate_evaluation_prompt(self, post_data: Dict) -> str:
        """生成评估提示词"""
        title = post_data.get('title', '')
        content = post_data.get('content', '')[:500]  # 限制长度

        prompt = f"""
请评估以下帖子是否与"大模型对IT行业就业岗位和职业技能的影响"这个主题相关。

【帖子信息】
- 标题: {title}
- 内容摘要: {content}

【评估标准】
1. 是否明确讨论大模型/AI（如ChatGPT、GPT、Claude等）？
2. 是否涉及IT行业从业者（程序员、开发者、工程师）？
3. 是否讨论了岗位变化、就业影响或技能要求？

【输出格式】
请以JSON格式输出评估结果：
{{
  "is_relevant": true/false,
  "score": 0.0-1.0,
  "reasons": ["原因1", "原因2"],
  "confidence": 0.0-1.0
}}

注意：如果帖子只是广告、推广或课程售卖，应标记为不相关。
"""
        return prompt

    def batch_evaluate(self, posts: List[Dict], method: str = 'simple') -> List[RelevanceScore]:
        """
        批量评估

        Args:
            posts: 帖子列表
            method: 评估方法（simple/ai_assisted）

        Returns:
            评分列表
        """
        results = []

        for post in posts:
            if method == 'simple':
                score = self.evaluate_post_simple(post)
                results.append(score)
            elif method == 'ai_assisted':
                # AI辅助评估需要逐个处理
                logger.info(f"评估: {post.get('title', 'Unknown')}")
                result = self.evaluate_post_ai_assisted(post)
                results.append(result)

        return results

    def generate_evaluation_report(self, scores: List[RelevanceScore]) -> str:
        """生成评估报告"""
        relevant_count = sum(1 for s in scores if s.is_relevant)
        avg_score = sum(s.score for s in scores) / len(scores) if scores else 0

        report = f"""
=== 相关性评估报告 ===

总帖子数: {len(scores)}
相关帖子数: {relevant_count}
平均得分: {avg_score:.2f}

【相关帖子列表】
"""
        for i, score in enumerate([s for s in scores if s.is_relevant], 1):
            report += f"\n{i}. {score.url}"
            report += f"\n   得分: {score.score:.2f} | 原因: {', '.join(score.reasons)}\n"

        report += "\n【不相关帖子列表】\n"
        for i, score in enumerate([s for s in scores if not s.is_relevant], 1):
            report += f"\n{i}. {score.url}"
            report += f"\n   原因: {', '.join(score.reasons)}\n"

        return report
