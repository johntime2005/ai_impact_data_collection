#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本分析 - 关键词提取和主题分析
分析讨论内容中的关键主题和情感倾向
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import re

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


def load_all_posts():
    """加载所有有效的帖子数据"""
    data_dir = project_root / "data" / "raw"

    valid_files = [
        "posts_20251121_093153.json",
        "posts_20251121_091738.json",
        "merged_posts_20251121_133607.json",
        "reddit_post_2.json",
        "reddit_post_6.json",
        "reddit_post_7.json",
        "reddit_post_10.json"
    ]

    all_posts = []
    seen_urls = set()

    ai_keywords = [
        'chatgpt', 'gpt', 'ai', '大模型', '人工智能', 'llm',
        '程序员', 'it', '开发', '失业', '岗位', '技能',
        '职业', 'programmer', 'developer', 'job', 'deepseek',
        'software engineer', 'coding'
    ]

    for filename in valid_files:
        file_path = data_dir / filename
        if not file_path.exists():
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict):
                data = [data]

            for post in data:
                url = post.get('url', '')
                if url and url in seen_urls:
                    continue

                title = post.get('title', '').lower()
                content = post.get('content', '').lower()
                is_ai_related = any(kw in title or kw in content for kw in ai_keywords)

                if is_ai_related and url:
                    seen_urls.add(url)
                    all_posts.append(post)

        except Exception as e:
            pass

    return all_posts


def extract_keywords(posts):
    """提取和统计关键词"""
    # 定义关键词类别
    keyword_categories = {
        'AI技术': {
            'chatgpt': 'ChatGPT',
            'gpt': 'GPT',
            'ai': 'AI',
            '大模型': '大模型',
            '人工智能': '人工智能',
            'llm': 'LLM',
            'deepseek': 'DeepSeek',
            'claude': 'Claude',
            'gemini': 'Gemini'
        },
        '岗位影响': {
            '失业': '失业',
            '裁员': '裁员',
            'layoff': '裁员',
            '就业': '就业',
            'job': '工作',
            'career': '职业',
            '岗位': '岗位',
            'employment': '就业',
            'unemploy': '失业',
            'replace': '替代',
            '替代': '替代',
            '取代': '取代'
        },
        '技能需求': {
            '技能': '技能',
            'skill': '技能',
            '学习': '学习',
            'learn': '学习',
            '转型': '转型',
            'transition': '转型',
            'upskill': '技能提升',
            '培训': '培训',
            'training': '培训'
        },
        '程序员': {
            '程序员': '程序员',
            'programmer': '程序员',
            'developer': '开发者',
            '开发': '开发',
            'coder': '编程者',
            'engineer': '工程师',
            'software': '软件'
        },
        '情感词汇': {
            '焦虑': '焦虑',
            'anxiety': '焦虑',
            'worry': '担忧',
            '担心': '担心',
            'fear': '恐惧',
            'hopeful': '希望',
            'optimistic': '乐观',
            'pessimistic': '悲观'
        }
    }

    # 统计所有文本
    all_text = []
    for post in posts:
        text = post.get('title', '') + ' ' + post.get('content', '')
        # 添加评论内容（前100条）
        for comment in post.get('comments', [])[:100]:
            text += ' ' + comment.get('content', '')
        all_text.append(text.lower())

    combined_text = ' '.join(all_text)

    # 统计每个类别的关键词
    category_stats = {}
    for category, keywords in keyword_categories.items():
        stats = {}
        for keyword, display_name in keywords.items():
            count = combined_text.count(keyword.lower())
            if count > 0:
                stats[display_name] = count

        # 按出现次数排序
        category_stats[category] = dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))

    return category_stats


def analyze_sentiment(posts):
    """简单的情感分析"""
    positive_words = ['good', 'great', 'excellent', 'amazing', 'helpful', 'useful',
                     'positive', 'opportunity', 'improve', 'better', '好', '棒', '有用',
                     '机会', '提升', '进步', 'hopeful', 'optimistic']

    negative_words = ['bad', 'terrible', 'awful', 'useless', 'worry', 'fear',
                     'replace', 'lose', 'job loss', '失业', '担心', '焦虑',
                     '糟糕', '恐惧', '替代', 'anxiety', 'pessimistic']

    neutral_words = ['think', 'maybe', 'possible', 'consider', '可能', '也许', '考虑']

    sentiment_stats = {
        'positive': 0,
        'negative': 0,
        'neutral': 0,
        'total_posts': len(posts)
    }

    for post in posts:
        text = (post.get('title', '') + ' ' + post.get('content', '')).lower()

        pos_count = sum(text.count(word) for word in positive_words)
        neg_count = sum(text.count(word) for word in negative_words)
        neu_count = sum(text.count(word) for word in neutral_words)

        # 根据词频判断倾向
        if pos_count > neg_count and pos_count > neu_count:
            sentiment_stats['positive'] += 1
        elif neg_count > pos_count:
            sentiment_stats['negative'] += 1
        else:
            sentiment_stats['neutral'] += 1

    return sentiment_stats


def extract_job_mentions(posts):
    """提取被提及的职位类型"""
    job_keywords = {
        '前端开发': ['前端', 'frontend', 'front-end', 'react', 'vue', 'angular'],
        '后端开发': ['后端', 'backend', 'back-end', 'server', 'api'],
        '全栈开发': ['全栈', 'fullstack', 'full-stack'],
        '算法工程师': ['算法', 'algorithm', 'ml engineer', 'machine learning'],
        '数据分析': ['数据分析', 'data analyst', 'data science'],
        '产品经理': ['产品经理', 'product manager', 'pm'],
        'UI/UX设计': ['ui', 'ux', '设计师', 'designer'],
        '测试工程师': ['测试', 'test', 'qa', 'quality'],
        '运维工程师': ['运维', 'devops', 'sre', 'operations']
    }

    all_text = []
    for post in posts:
        text = post.get('title', '') + ' ' + post.get('content', '')
        for comment in post.get('comments', [])[:50]:
            text += ' ' + comment.get('content', '')
        all_text.append(text.lower())

    combined_text = ' '.join(all_text)

    job_stats = {}
    for job_type, keywords in job_keywords.items():
        count = sum(combined_text.count(kw.lower()) for kw in keywords)
        if count > 0:
            job_stats[job_type] = count

    # 按提及次数排序
    return dict(sorted(job_stats.items(), key=lambda x: x[1], reverse=True))


def generate_report(keyword_stats, sentiment_stats, job_stats):
    """生成文本分析报告"""
    output_dir = project_root / "outputs" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "text_analysis.txt"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("大模型对IT行业影响 - 文本分析报告\n")
        f.write("=" * 80 + "\n\n")

        # 关键词统计
        f.write("🔑 关键词统计\n")
        f.write("-" * 80 + "\n\n")

        for category, keywords in keyword_stats.items():
            f.write(f"【{category}】\n")
            for word, count in list(keywords.items())[:10]:  # 只显示前10个
                f.write(f"  {word}: {count}次\n")
            f.write("\n")

        # 情感分析
        f.write("😊 情感倾向分析\n")
        f.write("-" * 80 + "\n")
        total = sentiment_stats['total_posts']
        f.write(f"积极倾向: {sentiment_stats['positive']}篇 ({sentiment_stats['positive']/total*100:.1f}%)\n")
        f.write(f"消极倾向: {sentiment_stats['negative']}篇 ({sentiment_stats['negative']/total*100:.1f}%)\n")
        f.write(f"中性倾向: {sentiment_stats['neutral']}篇 ({sentiment_stats['neutral']/total*100:.1f}%)\n\n")

        # 职位提及
        f.write("💼 职位类型提及频率\n")
        f.write("-" * 80 + "\n")
        for job_type, count in job_stats.items():
            f.write(f"{job_type}: {count}次提及\n")
        f.write("\n")

        # 分析洞察
        f.write("💡 初步洞察\n")
        f.write("-" * 80 + "\n")

        # 最关注的AI技术
        ai_tech = keyword_stats.get('AI技术', {})
        if ai_tech:
            top_ai = list(ai_tech.items())[0]
            f.write(f"1. 最受关注的AI技术: {top_ai[0]} (提及{top_ai[1]}次)\n")

        # 主要担忧
        job_impact = keyword_stats.get('岗位影响', {})
        if job_impact:
            top_concern = list(job_impact.items())[0]
            f.write(f"2. 主要担忧: {top_concern[0]} (提及{top_concern[1]}次)\n")

        # 整体情感
        if sentiment_stats['negative'] > sentiment_stats['positive']:
            f.write(f"3. 整体情感倾向: 偏消极/担忧 (消极占比{sentiment_stats['negative']/total*100:.1f}%)\n")
        else:
            f.write(f"3. 整体情感倾向: 相对积极/理性 (积极占比{sentiment_stats['positive']/total*100:.1f}%)\n")

        f.write("\n")

    print(f"✅ 文本分析报告已生成: {report_path}")
    return report_path


def main():
    """主函数"""
    print("🔍 开始文本分析...")

    # 加载数据
    print("\n1️⃣ 加载数据...")
    posts = load_all_posts()
    print(f"   找到 {len(posts)} 个帖子")

    # 关键词提取
    print("\n2️⃣ 提取关键词...")
    keyword_stats = extract_keywords(posts)

    # 情感分析
    print("\n3️⃣ 分析情感倾向...")
    sentiment_stats = analyze_sentiment(posts)

    # 职位提及
    print("\n4️⃣ 统计职位提及...")
    job_stats = extract_job_mentions(posts)

    # 生成报告
    print("\n5️⃣ 生成报告...")
    report_path = generate_report(keyword_stats, sentiment_stats, job_stats)

    # 打印摘要
    print("\n" + "=" * 80)
    print("📊 文本分析摘要")
    print("=" * 80)

    # 最热关键词
    all_keywords = []
    for category, keywords in keyword_stats.items():
        all_keywords.extend(keywords.items())
    all_keywords.sort(key=lambda x: x[1], reverse=True)

    print("\n🔥 热门关键词 TOP 5:")
    for i, (word, count) in enumerate(all_keywords[:5], 1):
        print(f"  {i}. {word}: {count}次")

    print(f"\n😊 情感分布:")
    total = sentiment_stats['total_posts']
    print(f"  积极: {sentiment_stats['positive']/total*100:.1f}% | "
          f"消极: {sentiment_stats['negative']/total*100:.1f}% | "
          f"中性: {sentiment_stats['neutral']/total*100:.1f}%")

    print(f"\n详细报告已保存至:")
    print(f"  {report_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
