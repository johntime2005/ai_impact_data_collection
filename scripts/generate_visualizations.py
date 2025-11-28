#!/usr/bin/env python3
"""可视化生成脚本 - 生成分析图表"""

import json
from pathlib import Path
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# 设置中文字体 - Windows系统
import matplotlib.font_manager as fm

# 尝试找到可用的中文字体
def get_chinese_font():
    """获取可用的中文字体"""
    font_names = ['Microsoft YaHei', 'SimHei', 'SimSun', 'NSimSun', 'FangSong', 'KaiTi']
    available_fonts = [f.name for f in fm.fontManager.ttflist]

    for font_name in font_names:
        if font_name in available_fonts:
            return font_name
    return 'DejaVu Sans'  # 回退选项

chinese_font = get_chinese_font()
matplotlib.rcParams['font.sans-serif'] = [chinese_font, 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
print(f"使用字体: {chinese_font}")

# 设置图表样式
plt.style.use('seaborn-v0_8-whitegrid')


def load_data():
    """加载所有分析数据"""
    processed_dir = Path("data/processed")
    analysis_dir = Path("data/analysis")

    with open(processed_dir / "merged_posts.json", 'r', encoding='utf-8') as f:
        posts = json.load(f)

    with open(processed_dir / "all_comments.json", 'r', encoding='utf-8') as f:
        comments = json.load(f)

    with open(processed_dir / "data_statistics.json", 'r', encoding='utf-8') as f:
        statistics = json.load(f)

    with open(analysis_dir / "text_analysis_results.json", 'r', encoding='utf-8') as f:
        analysis = json.load(f)

    with open(analysis_dir / "keywords_for_wordcloud.json", 'r', encoding='utf-8') as f:
        keywords = json.load(f)

    return posts, comments, statistics, analysis, keywords


def create_platform_distribution(statistics, output_dir):
    """创建平台分布图"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    platforms = list(statistics['platform_distribution'].keys())
    posts_counts = [statistics['platform_distribution'][p]['posts'] for p in platforms]
    comments_counts = [statistics['platform_distribution'][p]['comments'] for p in platforms]

    colors = ['#FF6B6B', '#4ECDC4']

    # 帖子分布饼图
    axes[0].pie(posts_counts, labels=[p.upper() for p in platforms], autopct='%1.1f%%',
                colors=colors, explode=[0.05] * len(platforms), shadow=True,
                textprops={'fontsize': 12})
    axes[0].set_title('帖子平台分布\nPost Distribution by Platform', fontsize=14, fontweight='bold')

    # 评论分布饼图
    axes[1].pie(comments_counts, labels=[p.upper() for p in platforms], autopct='%1.1f%%',
                colors=colors, explode=[0.05] * len(platforms), shadow=True,
                textprops={'fontsize': 12})
    axes[1].set_title('评论平台分布\nComment Distribution by Platform', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_dir / 'platform_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] platform_distribution.png")


def create_year_distribution(statistics, output_dir):
    """创建年份分布图"""
    fig, ax = plt.subplots(figsize=(10, 6))

    years = list(statistics['year_distribution'].keys())
    counts = list(statistics['year_distribution'].values())

    colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(years)))
    bars = ax.bar(years, counts, color=colors, edgecolor='navy', linewidth=1.5)

    # 添加数值标签
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                str(count), ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_xlabel('年份 / Year', fontsize=12)
    ax.set_ylabel('帖子数量 / Number of Posts', fontsize=12)
    ax.set_title('帖子年份分布（2022-2025）\nPost Distribution by Year', fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(counts) * 1.2)

    plt.tight_layout()
    plt.savefig(output_dir / 'year_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] year_distribution.png")


def create_sentiment_analysis(analysis, output_dir):
    """创建情感分析图"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 英文情感分布
    en_sentiment = analysis['sentiment']['english']['distribution']
    labels = ['Positive\n积极', 'Neutral\n中性', 'Negative\n消极']
    en_values = [en_sentiment.get('positive', 0), en_sentiment.get('neutral', 0), en_sentiment.get('negative', 0)]
    colors = ['#2ECC71', '#95A5A6', '#E74C3C']

    axes[0].bar(labels, en_values, color=colors, edgecolor='black', linewidth=1)
    for i, v in enumerate(en_values):
        axes[0].text(i, v + 5, str(v), ha='center', fontsize=11, fontweight='bold')
    axes[0].set_title(f'英文内容情感分布\nEnglish Sentiment\n(Avg Score: {analysis["sentiment"]["english"]["average_score"]:.3f})',
                      fontsize=13, fontweight='bold')
    axes[0].set_ylabel('数量 / Count', fontsize=11)

    # 中文情感分布
    zh_sentiment = analysis['sentiment']['chinese']['distribution']
    zh_values = [zh_sentiment.get('positive', 0), zh_sentiment.get('neutral', 0), zh_sentiment.get('negative', 0)]

    axes[1].bar(labels, zh_values, color=colors, edgecolor='black', linewidth=1)
    for i, v in enumerate(zh_values):
        axes[1].text(i, v + 1, str(v), ha='center', fontsize=11, fontweight='bold')
    axes[1].set_title(f'中文内容情感分布\nChinese Sentiment\n(Avg Score: {analysis["sentiment"]["chinese"]["average_score"]:.3f})',
                      fontsize=13, fontweight='bold')
    axes[1].set_ylabel('数量 / Count', fontsize=11)

    plt.tight_layout()
    plt.savefig(output_dir / 'sentiment_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] sentiment_analysis.png")


def create_topic_distribution(analysis, output_dir):
    """创建主题分布图"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    topic_labels = {
        'job_replacement': '工作替代\nJob Replacement',
        'skill_requirements': '技能需求\nSkill Requirements',
        'career_development': '职业发展\nCareer Development',
        'ai_tools': 'AI工具\nAI Tools',
        'industry_impact': '行业影响\nIndustry Impact',
        'emotional_response': '情绪反应\nEmotional Response'
    }

    colors = plt.cm.Set3(np.linspace(0, 1, 6))

    # 英文主题分布
    en_topics = analysis['topics']['english']
    en_labels = [topic_labels[k] for k in en_topics.keys()]
    en_values = [v['count'] for v in en_topics.values()]

    bars1 = axes[0].barh(en_labels, en_values, color=colors, edgecolor='black')
    for bar, v in zip(bars1, en_values):
        axes[0].text(v + 2, bar.get_y() + bar.get_height()/2, str(v),
                     ha='left', va='center', fontsize=10, fontweight='bold')
    axes[0].set_title('英文内容主题分布\nEnglish Topic Distribution', fontsize=13, fontweight='bold')
    axes[0].set_xlabel('提及次数 / Mention Count', fontsize=11)

    # 中文主题分布
    zh_topics = analysis['topics']['chinese']
    zh_values = [v['count'] for v in zh_topics.values()]

    bars2 = axes[1].barh(en_labels, zh_values, color=colors, edgecolor='black')
    for bar, v in zip(bars2, zh_values):
        axes[1].text(v + 0.5, bar.get_y() + bar.get_height()/2, str(v),
                     ha='left', va='center', fontsize=10, fontweight='bold')
    axes[1].set_title('中文内容主题分布\nChinese Topic Distribution', fontsize=13, fontweight='bold')
    axes[1].set_xlabel('提及次数 / Mention Count', fontsize=11)

    plt.tight_layout()
    plt.savefig(output_dir / 'topic_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] topic_distribution.png")


def create_keyword_chart(keywords, output_dir):
    """创建关键词图表"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # 英文关键词 Top 20
    en_kw = list(keywords['english'].items())[:20]
    en_words = [kw[0] for kw in en_kw][::-1]
    en_counts = [kw[1] for kw in en_kw][::-1]

    colors_en = plt.cm.Blues(np.linspace(0.3, 0.9, len(en_words)))
    axes[0].barh(en_words, en_counts, color=colors_en, edgecolor='navy')
    axes[0].set_title('英文高频关键词 Top 20\nTop 20 English Keywords', fontsize=13, fontweight='bold')
    axes[0].set_xlabel('出现频次 / Frequency', fontsize=11)

    # 中文关键词 Top 20
    zh_kw = list(keywords['chinese'].items())[:20]
    zh_words = [kw[0] for kw in zh_kw][::-1]
    zh_counts = [kw[1] for kw in zh_kw][::-1]

    colors_zh = plt.cm.Reds(np.linspace(0.3, 0.9, len(zh_words)))
    axes[1].barh(zh_words, zh_counts, color=colors_zh, edgecolor='darkred')
    axes[1].set_title('中文高频关键词 Top 20\nTop 20 Chinese Keywords', fontsize=13, fontweight='bold')
    axes[1].set_xlabel('出现频次 / Frequency', fontsize=11)

    plt.tight_layout()
    plt.savefig(output_dir / 'keyword_frequency.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] keyword_frequency.png")


def create_time_trend(analysis, output_dir):
    """创建时间趋势图"""
    fig, ax = plt.subplots(figsize=(10, 6))

    time_trend = analysis['time_trend']
    years = sorted(time_trend.keys())
    sentiments = [time_trend[y]['avg_sentiment'] for y in years]
    counts = [time_trend[y]['count'] for y in years]

    # 双轴图
    ax2 = ax.twinx()

    # 情感趋势线
    line1 = ax.plot(years, sentiments, 'o-', color='#E74C3C', linewidth=2.5,
                    markersize=10, label='情感得分 Sentiment Score')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('年份 / Year', fontsize=12)
    ax.set_ylabel('平均情感得分 / Avg Sentiment Score', fontsize=12, color='#E74C3C')
    ax.tick_params(axis='y', labelcolor='#E74C3C')
    ax.set_ylim(-1.2, 0.5)

    # 帖子数量柱状图
    bars = ax2.bar(years, counts, alpha=0.3, color='#3498DB', label='帖子数量 Post Count')
    ax2.set_ylabel('帖子数量 / Post Count', fontsize=12, color='#3498DB')
    ax2.tick_params(axis='y', labelcolor='#3498DB')

    # 添加数值标签
    for year, sentiment, count in zip(years, sentiments, counts):
        ax.annotate(f'{sentiment:.2f}', (year, sentiment), textcoords="offset points",
                   xytext=(0, 10), ha='center', fontsize=10, color='#E74C3C', fontweight='bold')

    ax.set_title('情感趋势随时间变化（2022-2025）\nSentiment Trend Over Time', fontsize=14, fontweight='bold')

    # 图例
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    plt.tight_layout()
    plt.savefig(output_dir / 'time_trend.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] time_trend.png")


def create_overview_dashboard(statistics, analysis, output_dir):
    """创建总览仪表板"""
    fig = plt.figure(figsize=(16, 12))

    # 定义网格
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 1. 数据概览 (左上)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis('off')
    overview_text = f"""
    📊 数据概览
    ━━━━━━━━━━━━━━━
    总帖子数: {statistics['total_posts']}
    总评论数: {statistics['total_comments']}
    平均评论: {statistics['avg_comments_per_post']}/帖

    时间跨度:
    {statistics['date_range']['earliest']}
    至 {statistics['date_range']['latest']}
    """
    ax1.text(0.1, 0.5, overview_text, fontsize=12, verticalalignment='center',
             fontfamily='monospace', transform=ax1.transAxes,
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    ax1.set_title('Data Overview', fontsize=13, fontweight='bold')

    # 2. 平台分布 (中上)
    ax2 = fig.add_subplot(gs[0, 1])
    platforms = list(statistics['platform_distribution'].keys())
    posts_counts = [statistics['platform_distribution'][p]['posts'] for p in platforms]
    ax2.pie(posts_counts, labels=[p.upper() for p in platforms], autopct='%1.1f%%',
            colors=['#FF6B6B', '#4ECDC4'], explode=[0.05] * len(platforms))
    ax2.set_title('平台分布 / Platform', fontsize=13, fontweight='bold')

    # 3. 年份分布 (右上)
    ax3 = fig.add_subplot(gs[0, 2])
    years = list(statistics['year_distribution'].keys())
    counts = list(statistics['year_distribution'].values())
    ax3.bar(years, counts, color=plt.cm.Blues(np.linspace(0.4, 0.8, len(years))))
    ax3.set_title('年份分布 / Year', fontsize=13, fontweight='bold')
    ax3.set_ylabel('帖子数')

    # 4. 英文情感分布 (左中)
    ax4 = fig.add_subplot(gs[1, 0])
    en_sentiment = analysis['sentiment']['english']['distribution']
    labels = ['Positive', 'Neutral', 'Negative']
    en_values = [en_sentiment.get('positive', 0), en_sentiment.get('neutral', 0), en_sentiment.get('negative', 0)]
    ax4.bar(labels, en_values, color=['#2ECC71', '#95A5A6', '#E74C3C'])
    ax4.set_title('英文情感 / EN Sentiment', fontsize=13, fontweight='bold')

    # 5. 中文情感分布 (中中)
    ax5 = fig.add_subplot(gs[1, 1])
    zh_sentiment = analysis['sentiment']['chinese']['distribution']
    zh_values = [zh_sentiment.get('positive', 0), zh_sentiment.get('neutral', 0), zh_sentiment.get('negative', 0)]
    ax5.bar(labels, zh_values, color=['#2ECC71', '#95A5A6', '#E74C3C'])
    ax5.set_title('中文情感 / ZH Sentiment', fontsize=13, fontweight='bold')

    # 6. 情感对比 (右中)
    ax6 = fig.add_subplot(gs[1, 2])
    langs = ['English', 'Chinese']
    avg_scores = [analysis['sentiment']['english']['average_score'],
                  analysis['sentiment']['chinese']['average_score']]
    colors = ['#3498DB' if s >= 0 else '#E74C3C' for s in avg_scores]
    ax6.barh(langs, avg_scores, color=colors)
    ax6.axvline(x=0, color='gray', linestyle='--')
    ax6.set_xlim(-0.5, 0.5)
    ax6.set_title('情感得分对比 / Sentiment Comparison', fontsize=13, fontweight='bold')

    # 7. 英文主题分布 (左下)
    ax7 = fig.add_subplot(gs[2, 0])
    en_topics = analysis['topics']['english']
    topic_names = ['Replace', 'Skills', 'Career', 'Tools', 'Industry', 'Emotion']
    en_topic_values = [v['count'] for v in en_topics.values()]
    ax7.barh(topic_names, en_topic_values, color=plt.cm.Set3(np.linspace(0, 1, 6)))
    ax7.set_title('英文主题 / EN Topics', fontsize=13, fontweight='bold')

    # 8. 中文主题分布 (中下)
    ax8 = fig.add_subplot(gs[2, 1])
    zh_topics = analysis['topics']['chinese']
    zh_topic_values = [v['count'] for v in zh_topics.values()]
    ax8.barh(topic_names, zh_topic_values, color=plt.cm.Set3(np.linspace(0, 1, 6)))
    ax8.set_title('中文主题 / ZH Topics', fontsize=13, fontweight='bold')

    # 9. 时间趋势 (右下)
    ax9 = fig.add_subplot(gs[2, 2])
    time_trend = analysis['time_trend']
    trend_years = sorted(time_trend.keys())
    trend_sentiments = [time_trend[y]['avg_sentiment'] for y in trend_years]
    ax9.plot(trend_years, trend_sentiments, 'o-', color='#E74C3C', linewidth=2, markersize=8)
    ax9.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax9.set_title('情感趋势 / Trend', fontsize=13, fontweight='bold')
    ax9.set_ylabel('Sentiment Score')

    fig.suptitle('AI对IT行业就业影响分析 - 数据总览\nAI Impact on IT Employment - Dashboard',
                 fontsize=16, fontweight='bold', y=0.98)

    plt.savefig(output_dir / 'overview_dashboard.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] overview_dashboard.png")


def create_wordcloud_alternative(keywords, output_dir):
    """创建词云替代图（气泡图）"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # 英文关键词气泡图
    en_kw = list(keywords['english'].items())[:30]
    en_words = [kw[0] for kw in en_kw]
    en_counts = [kw[1] for kw in en_kw]

    # 随机位置
    np.random.seed(42)
    x_en = np.random.rand(len(en_words)) * 10
    y_en = np.random.rand(len(en_words)) * 10
    sizes_en = [c * 20 for c in en_counts]

    scatter1 = axes[0].scatter(x_en, y_en, s=sizes_en, alpha=0.6,
                                c=range(len(en_words)), cmap='Blues')
    for i, word in enumerate(en_words):
        axes[0].annotate(word, (x_en[i], y_en[i]), ha='center', va='center',
                        fontsize=8 + en_counts[i] // 20)
    axes[0].set_xlim(-1, 11)
    axes[0].set_ylim(-1, 11)
    axes[0].axis('off')
    axes[0].set_title('英文关键词云 / English Keywords', fontsize=14, fontweight='bold')

    # 中文关键词气泡图
    zh_kw = list(keywords['chinese'].items())[:25]
    zh_words = [kw[0] for kw in zh_kw]
    zh_counts = [kw[1] for kw in zh_kw]

    x_zh = np.random.rand(len(zh_words)) * 10
    y_zh = np.random.rand(len(zh_words)) * 10
    sizes_zh = [c * 50 for c in zh_counts]

    scatter2 = axes[1].scatter(x_zh, y_zh, s=sizes_zh, alpha=0.6,
                                c=range(len(zh_words)), cmap='Reds')
    for i, word in enumerate(zh_words):
        axes[1].annotate(word, (x_zh[i], y_zh[i]), ha='center', va='center',
                        fontsize=8 + zh_counts[i] // 3)
    axes[1].set_xlim(-1, 11)
    axes[1].set_ylim(-1, 11)
    axes[1].axis('off')
    axes[1].set_title('中文关键词云 / Chinese Keywords', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_dir / 'keyword_cloud.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  [OK] keyword_cloud.png")


def main():
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    output_dir = Path("data/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Visualization Generation")
    print("=" * 60)

    print("\nLoading data...")
    posts, comments, statistics, analysis, keywords = load_data()
    print("  [OK] Data loaded")

    print("\nGenerating charts...")

    # Generate charts
    create_platform_distribution(statistics, output_dir)
    create_year_distribution(statistics, output_dir)
    create_sentiment_analysis(analysis, output_dir)
    create_topic_distribution(analysis, output_dir)
    create_keyword_chart(keywords, output_dir)
    create_time_trend(analysis, output_dir)
    create_overview_dashboard(statistics, analysis, output_dir)
    create_wordcloud_alternative(keywords, output_dir)

    print(f"\n[OK] All charts saved to: {output_dir}")
    print("\nGenerated charts:")
    for f in output_dir.glob("*.png"):
        print(f"  - {f.name}")

    print("\n" + "=" * 60)
    print("[OK] Visualization complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
