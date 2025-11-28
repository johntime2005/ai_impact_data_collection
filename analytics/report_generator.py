"""
报告生成模块 - 生成Markdown格式的分析报告
"""
from typing import List, Dict
from datetime import datetime
from pathlib import Path
import sys
import os
from loguru import logger

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.report_parts = []

    def generate_report(
        self,
        posts: List[Dict],
        quality_analysis: Dict,
        text_analysis: Dict,
        output_path: Path
    ) -> Path:
        """
        生成完整的分析报告

        Args:
            posts: 帖子数据
            quality_analysis: 质量分析结果
            text_analysis: 文本分析结果
            output_path: 输出路径

        Returns:
            报告文件路径
        """
        logger.info("开始生成分析报告")

        # 清空之前的内容
        self.report_parts = []

        # 1. 报告头部
        self._add_header()

        # 2. 数据概览
        self._add_data_overview(posts, quality_analysis)

        # 3. 质量分析
        self._add_quality_analysis(quality_analysis)

        # 4. 文本分析
        self._add_text_analysis(text_analysis)

        # 5. 数据源列表
        self._add_data_sources(posts)

        # 6. 结论和建议
        self._add_conclusion(quality_analysis)

        # 写入文件
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report_content = '\n\n'.join(self.report_parts)
        output_path.write_text(report_content, encoding='utf-8')

        logger.info(f"报告已生成: {output_path}")
        return output_path

    def _add_header(self):
        """添加报告头部"""
        header = f"""# 大模型对IT行业影响数据采集报告

**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

**报告说明**: 本报告基于从知乎、V2EX等社区采集的讨论数据，分析大模型（ChatGPT等）对IT行业就业岗位和职业技能的影响。

---
"""
        self.report_parts.append(header)

    def _add_data_overview(self, posts: List[Dict], quality_analysis: Dict):
        """添加数据概览"""
        basic = quality_analysis.get('basic_stats', {})
        platform_dist = quality_analysis.get('platform_distribution', {})

        overview = f"""## 一、数据概览

### 1.1 数据规模

- **总帖子数**: {basic.get('total_posts', 0)} 条
- **有效帖子数**: {basic.get('valid_posts', 0)} 条 (评论≥100)
- **总评论数**: {basic.get('total_comments', 0)} 条
- **平均每帖评论数**: {basic.get('avg_comments_per_post', 0):.1f} 条

### 1.2 数据来源

| 平台 | 帖子数 | 占比 |
|------|--------|------|"""

        platforms = platform_dist.get('platforms', {})
        percentages = platform_dist.get('platform_percentages', {})

        for platform, count in platforms.items():
            percentage = percentages.get(platform, 0)
            overview += f"\n| {platform.upper()} | {count} | {percentage:.1f}% |"

        self.report_parts.append(overview)

    def _add_quality_analysis(self, quality_analysis: Dict):
        """添加质量分析"""
        quality = quality_analysis.get('quality_checks', {})
        time_dist = quality_analysis.get('time_distribution', {})
        comment_stats = quality_analysis.get('comment_stats', {})

        analysis = f"""## 二、数据质量分析

### 2.1 质量评分

**总体质量得分**: {quality.get('overall_quality_score', 0):.1f} / 100

### 2.2 质量指标

| 指标 | 结果 | 状态 |
|------|------|------|
| 满足最少帖子数要求 | {quality.get('meets_min_posts', False)} | {'✓ 通过' if quality.get('meets_min_posts', False) else '✗ 不通过'} |
| 满足最少评论数要求 | {quality.get('meets_min_comments', False)} | {'✓ 通过' if quality.get('meets_min_comments', False) else '✗ 不通过'} |
| 包含时间信息 | {quality.get('has_time_info', 0):.1f}% | {'✓ 良好' if quality.get('has_time_info', 0) > 80 else '⚠️ 中等' if quality.get('has_time_info', 0) > 50 else '✗ 较差'} |
| 包含作者信息 | {quality.get('has_author_info', 0):.1f}% | {'✓ 良好' if quality.get('has_author_info', 0) > 80 else '⚠️ 中等' if quality.get('has_author_info', 0) > 50 else '✗ 较差'} |

### 2.3 时间分布

| 时间段 | 帖子数 |
|--------|--------|"""

        time_periods = time_dist.get('time_periods', {})
        for period, count in time_periods.items():
            analysis += f"\n| {period} | {count} |"

        analysis += f"""

### 2.4 评论质量

- **总评论数**: {comment_stats.get('total_comments', 0)} 条
- **平均评论长度**: {comment_stats.get('avg_length', 0):.0f} 字符
- **高质量评论数**: {comment_stats.get('high_quality_count', 0)} 条 ({comment_stats.get('high_quality_percentage', 0):.1f}%)
  - *高质量定义: 点赞数>10 且 长度>50字符*
"""

        self.report_parts.append(analysis)

    def _add_text_analysis(self, text_analysis: Dict):
        """添加文本分析"""
        keyword_freq = text_analysis.get('keyword_frequency', {})
        word_freq = text_analysis.get('word_frequency', [])
        sentiment = text_analysis.get('sentiment_distribution', {})

        analysis = f"""## 三、文本分析

### 3.1 关键词覆盖

#### 主关键词出现频次

| 关键词 | 出现次数 |
|--------|----------|"""

        primary_keywords = keyword_freq.get('primary', {})
        for keyword, count in sorted(primary_keywords.items(), key=lambda x: x[1], reverse=True):
            analysis += f"\n| {keyword} | {count} |"

        analysis += "\n\n#### 次关键词出现频次\n\n| 关键词 | 出现次数 |\n|--------|----------|"

        secondary_keywords = keyword_freq.get('secondary', {})
        for keyword, count in sorted(secondary_keywords.items(), key=lambda x: x[1], reverse=True)[:10]:
            analysis += f"\n| {keyword} | {count} |"

        analysis += f"""

### 3.2 高频词汇 (Top 20)

| 排名 | 词汇 | 频次 |
|------|------|------|"""

        for i, (word, count) in enumerate(word_freq[:20], 1):
            analysis += f"\n| {i} | {word} | {count} |"

        analysis += f"""

### 3.3 情感倾向分析

| 情感 | 数量 | 占比 |
|------|------|------|
| 积极 | {sentiment.get('positive', 0)} | {sentiment.get('positive_percentage', 0):.1f}% |
| 消极 | {sentiment.get('negative', 0)} | {sentiment.get('negative_percentage', 0):.1f}% |
| 中性 | {sentiment.get('neutral', 0)} | {sentiment.get('neutral_percentage', 0):.1f}% |

**注**: 情感分析基于简单的关键词匹配，仅供参考。
"""

        self.report_parts.append(analysis)

    def _add_data_sources(self, posts: List[Dict]):
        """添加数据源列表"""
        sources = """## 四、数据源详情

### 4.1 采集的帖子列表

| # | 平台 | 标题 | 评论数 | URL |
|---|------|------|--------|-----|"""

        for i, post in enumerate(posts, 1):
            platform = post.get('platform', 'unknown').upper()
            title = post.get('title', '未知标题')[:50]  # 限制标题长度
            comment_count = len(post.get('comments', []))
            url = post.get('url', '')

            sources += f"\n| {i} | {platform} | {title} | {comment_count} | {url} |"

        self.report_parts.append(sources)

    def _add_conclusion(self, quality_analysis: Dict):
        """添加结论和建议"""
        quality_score = quality_analysis.get('quality_checks', {}).get('overall_quality_score', 0)

        if quality_score >= 80:
            quality_assessment = "优秀"
            recommendation = "数据质量优秀，可以进行深入分析。建议进一步进行情感分析、主题建模等高级分析。"
        elif quality_score >= 60:
            quality_assessment = "良好"
            recommendation = "数据质量良好，基本满足分析需求。建议补充部分时间段或平台的数据以提高全面性。"
        else:
            quality_assessment = "待改进"
            recommendation = "数据质量有待改进。建议增加采集的帖子数量，并确保每个帖子的评论数达标。"

        conclusion = f"""## 五、结论与建议

### 5.1 数据质量评估

本次数据采集的整体质量为 **{quality_assessment}**（得分: {quality_score:.1f}/100）。

### 5.2 建议

{recommendation}

### 5.3 后续分析方向

1. **情感分析**: 使用专业的NLP工具进行更精确的情感分析
2. **主题建模**: 使用LDA等方法提取讨论的主要主题
3. **时间序列分析**: 分析讨论热度和情感的时间变化趋势
4. **影响力分析**: 分析高赞评论和高影响力作者的观点
5. **技能需求分析**: 提取和统计提到的具体技能和岗位要求

---

*报告生成完毕*
"""

        self.report_parts.append(conclusion)
