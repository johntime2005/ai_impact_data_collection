#!/usr/bin/env python3
"""文本分析脚本 - 关键词提取与情感分析"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

# 中文停用词
CHINESE_STOPWORDS = set([
    '的', '了', '是', '我', '你', '他', '她', '它', '们', '这', '那', '有', '在', '不', '就', '也',
    '都', '和', '与', '或', '但', '而', '如果', '因为', '所以', '虽然', '但是', '可以', '能够',
    '已经', '正在', '将要', '会', '要', '能', '想', '觉得', '知道', '看', '说', '做', '去', '来',
    '很', '非常', '太', '最', '更', '还', '又', '再', '只', '就是', '什么', '怎么', '为什么',
    '哪', '谁', '多少', '几', '一个', '这个', '那个', '一些', '某些', '其他', '自己', '大家',
    '没有', '不是', '不会', '不能', '没', '吧', '呢', '啊', '吗', '呀', '嘛', '哦', '哈',
    '上', '下', '中', '里', '外', '前', '后', '左', '右', '东', '西', '南', '北',
    '年', '月', '日', '时', '分', '秒', '个', '只', '条', '件', '种', '位', '名',
])

# 英文停用词
ENGLISH_STOPWORDS = set([
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
    'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
    'shall', 'can', 'need', 'dare', 'ought', 'used', 'i', 'you', 'he', 'she', 'it',
    'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our',
    'their', 'mine', 'yours', 'hers', 'ours', 'theirs', 'this', 'that', 'these', 'those',
    'what', 'which', 'who', 'whom', 'whose', 'when', 'where', 'why', 'how', 'all', 'each',
    'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now', 'here',
    'there', 'then', 'once', 'if', 'because', 'although', 'though', 'while', 'until',
    'unless', 'since', 'after', 'before', 'about', 'into', 'through', 'during', 'above',
    'below', 'between', 'under', 'again', 'further', 'any', 'am', 'being', 'get', 'got',
    'getting', 'going', 'go', 'goes', 'went', 'come', 'comes', 'came', 'coming', 'make',
    'makes', 'made', 'making', 'take', 'takes', 'took', 'taking', 'see', 'sees', 'saw',
    'seeing', 'know', 'knows', 'knew', 'knowing', 'think', 'thinks', 'thought', 'thinking',
    'want', 'wants', 'wanted', 'wanting', 'use', 'uses', 'used', 'using', 'find', 'finds',
    'found', 'finding', 'give', 'gives', 'gave', 'giving', 'tell', 'tells', 'told', 'telling',
    'work', 'works', 'worked', 'working', 'seem', 'seems', 'seemed', 'seeming', 'feel',
    'feels', 'felt', 'feeling', 'try', 'tries', 'tried', 'trying', 'leave', 'leaves',
    'left', 'leaving', 'call', 'calls', 'called', 'calling', 'keep', 'keeps', 'kept',
    'keeping', 'let', 'lets', 'letting', 'begin', 'begins', 'began', 'beginning', 'show',
    'shows', 'showed', 'showing', 'hear', 'hears', 'heard', 'hearing', 'play', 'plays',
    'played', 'playing', 'run', 'runs', 'ran', 'running', 'move', 'moves', 'moved', 'moving',
    'like', 'likes', 'liked', 'liking', 'live', 'lives', 'lived', 'living', 'believe',
    'believes', 'believed', 'believing', 'hold', 'holds', 'held', 'holding', 'bring',
    'brings', 'brought', 'bringing', 'happen', 'happens', 'happened', 'happening', 'write',
    'writes', 'wrote', 'writing', 'provide', 'provides', 'provided', 'providing', 'sit',
    'sits', 'sat', 'sitting', 'stand', 'stands', 'stood', 'standing', 'lose', 'loses',
    'lost', 'losing', 'pay', 'pays', 'paid', 'paying', 'meet', 'meets', 'met', 'meeting',
    'include', 'includes', 'included', 'including', 'continue', 'continues', 'continued',
    'set', 'sets', 'setting', 'learn', 'learns', 'learned', 'learning', 'change', 'changes',
    'changed', 'changing', 'lead', 'leads', 'led', 'leading', 'understand', 'understands',
    'understood', 'understanding', 'watch', 'watches', 'watched', 'watching', 'follow',
    'follows', 'followed', 'following', 'stop', 'stops', 'stopped', 'stopping', 'create',
    'creates', 'created', 'creating', 'speak', 'speaks', 'spoke', 'speaking', 'read',
    'reads', 'reading', 'allow', 'allows', 'allowed', 'allowing', 'add', 'adds', 'added',
    'adding', 'spend', 'spends', 'spent', 'spending', 'grow', 'grows', 'grew', 'growing',
    'open', 'opens', 'opened', 'opening', 'walk', 'walks', 'walked', 'walking', 'win',
    'wins', 'won', 'winning', 'offer', 'offers', 'offered', 'offering', 'remember',
    'remembers', 'remembered', 'remembering', 'love', 'loves', 'loved', 'loving', 'consider',
    'considers', 'considered', 'considering', 'appear', 'appears', 'appeared', 'appearing',
    'buy', 'buys', 'bought', 'buying', 'wait', 'waits', 'waited', 'waiting', 'serve',
    'serves', 'served', 'serving', 'die', 'dies', 'died', 'dying', 'send', 'sends', 'sent',
    'sending', 'expect', 'expects', 'expected', 'expecting', 'build', 'builds', 'built',
    'building', 'stay', 'stays', 'stayed', 'staying', 'fall', 'falls', 'fell', 'falling',
    'cut', 'cuts', 'cutting', 'reach', 'reaches', 'reached', 'reaching', 'kill', 'kills',
    'killed', 'killing', 'remain', 'remains', 'remained', 'remaining', 'suggest', 'suggests',
    'suggested', 'suggesting', 'raise', 'raises', 'raised', 'raising', 'pass', 'passes',
    'passed', 'passing', 'sell', 'sells', 'sold', 'selling', 'require', 'requires',
    'required', 'requiring', 'report', 'reports', 'reported', 'reporting', 'decide',
    'decides', 'decided', 'deciding', 'pull', 'pulls', 'pulled', 'pulling', 'really',
    'even', 'back', 'still', 'well', 'way', 'new', 'first', 'last', 'long', 'great',
    'little', 'own', 'other', 'old', 'right', 'big', 'high', 'different', 'small', 'large',
    'next', 'early', 'young', 'important', 'few', 'public', 'bad', 'same', 'able', 'don',
    't', 's', 've', 're', 'll', 'd', 'm', 'isn', 'aren', 'wasn', 'weren', 'hasn', 'haven',
    'hadn', 'doesn', 'didn', 'won', 'wouldn', 'shan', 'shouldn', 'couldn', 'mustn', 'needn',
    'thing', 'things', 'something', 'anything', 'everything', 'nothing', 'someone', 'anyone',
    'everyone', 'no one', 'people', 'person', 'time', 'times', 'year', 'years', 'day', 'days',
    'week', 'weeks', 'month', 'months', 'lot', 'lots', 'much', 'many', 'bit', 'point',
    'yeah', 'yes', 'ok', 'okay', 'sure', 'actually', 'probably', 'maybe', 'definitely',
    'certainly', 'basically', 'literally', 'simply', 'just', 'exactly', 'especially',
    'particularly', 'specifically', 'generally', 'usually', 'often', 'sometimes', 'always',
    'never', 'ever', 'already', 'yet', 'soon', 'later', 'ago', 'today', 'tomorrow', 'yesterday',
    'etc', 'e', 'g', 'i', 'e'
])

# AI/编程相关关键词（用于提取）
AI_KEYWORDS = {
    'en': [
        'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 'neural network',
        'chatgpt', 'gpt', 'llm', 'large language model', 'openai', 'anthropic', 'claude', 'gemini',
        'copilot', 'github copilot', 'cursor', 'automation', 'automate', 'replace', 'replacement',
        'job', 'jobs', 'career', 'employment', 'unemployed', 'layoff', 'layoffs', 'hire', 'hiring',
        'programmer', 'programmers', 'developer', 'developers', 'engineer', 'engineers', 'coding',
        'software', 'tech', 'technology', 'skill', 'skills', 'learning', 'adapt', 'future',
        'junior', 'senior', 'entry level', 'mid level', 'experience', 'experienced',
        'productivity', 'efficient', 'efficiency', 'tool', 'tools', 'assistant', 'help',
        'code', 'coding', 'programming', 'develop', 'development', 'project', 'projects',
        'salary', 'salaries', 'income', 'market', 'industry', 'company', 'companies',
        'threat', 'opportunity', 'risk', 'benefit', 'impact', 'change', 'transform',
        'worry', 'worried', 'concern', 'concerned', 'fear', 'afraid', 'optimistic', 'pessimistic',
        'vibe coding', 'prompt engineering', 'agent', 'agents', 'agentic'
    ],
    'zh': [
        'ai', '人工智能', '机器学习', '深度学习', '神经网络', 'chatgpt', 'gpt', '大模型', '大语言模型',
        'openai', 'claude', 'gemini', 'copilot', '自动化', '取代', '替代', '淘汰',
        '工作', '职业', '就业', '失业', '裁员', '招聘', '程序员', '开发者', '工程师', '码农',
        '编程', '软件', '技术', '技能', '学习', '适应', '未来', '初级', '高级', '资深', '经验',
        '效率', '生产力', '工具', '助手', '代码', '开发', '项目', '薪资', '收入', '市场', '行业',
        '威胁', '机会', '风险', '好处', '影响', '变革', '转型', '担心', '焦虑', '恐惧', '乐观', '悲观',
        '35岁', '中年', '转行', '内卷', '躺平', '卷', '提示词', '智能体', 'agent'
    ]
}

# 情感词典
SENTIMENT_WORDS = {
    'positive': {
        'en': ['good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic', 'wonderful',
               'helpful', 'useful', 'beneficial', 'opportunity', 'opportunities', 'advantage',
               'improve', 'better', 'best', 'love', 'like', 'enjoy', 'happy', 'excited',
               'optimistic', 'positive', 'hope', 'hopeful', 'promising', 'success', 'successful',
               'efficient', 'productivity', 'innovative', 'creative', 'smart', 'intelligent',
               'powerful', 'capable', 'effective', 'valuable', 'progress', 'advance', 'growth',
               'assist', 'assistance', 'support', 'enhance', 'boost', 'augment', 'empower'],
        'zh': ['好', '很好', '非常好', '优秀', '出色', '棒', '厉害', '有用', '有帮助', '有益',
               '机会', '优势', '改善', '提升', '进步', '喜欢', '开心', '兴奋', '乐观', '积极',
               '希望', '有前途', '成功', '高效', '创新', '创造', '强大', '有效', '有价值',
               '辅助', '支持', '增强', '赋能', '解放', '效率']
    },
    'negative': {
        'en': ['bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike', 'angry',
               'sad', 'worried', 'worry', 'concern', 'concerned', 'fear', 'afraid', 'scary',
               'threat', 'threaten', 'threatening', 'danger', 'dangerous', 'risk', 'risky',
               'replace', 'replacement', 'obsolete', 'useless', 'worthless', 'unemployed',
               'unemployment', 'layoff', 'layoffs', 'fired', 'lose', 'lost', 'losing',
               'pessimistic', 'negative', 'doom', 'doomed', 'fail', 'failure', 'difficult',
               'hard', 'struggle', 'struggling', 'crisis', 'problem', 'problems', 'issue',
               'issues', 'decline', 'decrease', 'drop', 'fall', 'crash', 'collapse'],
        'zh': ['差', '糟糕', '可怕', '恐怖', '最差', '讨厌', '生气', '难过', '担心', '担忧',
               '焦虑', '恐惧', '害怕', '威胁', '危险', '风险', '取代', '替代', '淘汰', '过时',
               '无用', '失业', '裁员', '被裁', '失去', '悲观', '消极', '末日', '失败', '困难',
               '艰难', '挣扎', '危机', '问题', '下降', '减少', '崩溃', '内卷', '卷']
    }
}


def is_chinese(text: str) -> bool:
    """判断文本是否主要是中文"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(re.findall(r'\w', text))
    return chinese_chars > total_chars * 0.3 if total_chars > 0 else False


def tokenize_chinese(text: str) -> list:
    """简单的中文分词（基于字符和常见词组）"""
    # 提取中文词组和单字
    words = []

    # 首先尝试提取常见词组
    common_phrases = [
        '人工智能', '机器学习', '深度学习', '大语言模型', '大模型', '程序员', '软件工程师',
        '开发者', '工程师', '就业市场', '求职', '面试', '技术栈', '编程语言', '工作经验',
        '职业发展', '职业规划', '技能提升', '自我提升', '终身学习', '持续学习',
        '裁员', '失业', '内卷', '躺平', '35岁', '中年危机', '转行', '转型',
        '自动化', '智能化', '数字化', 'chatgpt', 'gpt', 'ai', 'copilot'
    ]

    text_lower = text.lower()
    for phrase in common_phrases:
        if phrase in text_lower:
            words.append(phrase)

    # 提取单个中文字符（作为备选）
    chinese_chars = re.findall(r'[\u4e00-\u9fff]+', text)
    for chars in chinese_chars:
        if len(chars) >= 2:
            words.append(chars)

    return words


def tokenize_english(text: str) -> list:
    """英文分词"""
    # 转小写并提取单词
    text = text.lower()
    words = re.findall(r'\b[a-z]+\b', text)
    return words


def extract_keywords(texts: list, language: str, top_n: int = 50) -> list:
    """提取关键词"""
    word_freq = Counter()

    stopwords = CHINESE_STOPWORDS if language == 'zh' else ENGLISH_STOPWORDS

    for text in texts:
        if language == 'zh':
            words = tokenize_chinese(text)
        else:
            words = tokenize_english(text)

        for word in words:
            word = word.lower().strip()
            if len(word) >= 2 and word not in stopwords:
                word_freq[word] += 1

    return word_freq.most_common(top_n)


def analyze_sentiment(text: str, language: str) -> dict:
    """分析文本情感"""
    text_lower = text.lower()

    positive_words = SENTIMENT_WORDS['positive'].get(language, [])
    negative_words = SENTIMENT_WORDS['negative'].get(language, [])

    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    total = positive_count + negative_count
    if total == 0:
        sentiment_score = 0
        sentiment_label = 'neutral'
    else:
        sentiment_score = (positive_count - negative_count) / total
        if sentiment_score > 0.2:
            sentiment_label = 'positive'
        elif sentiment_score < -0.2:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'

    return {
        'score': round(sentiment_score, 3),
        'label': sentiment_label,
        'positive_count': positive_count,
        'negative_count': negative_count
    }


def extract_topics(texts: list, language: str) -> dict:
    """提取主题分布"""
    topics = {
        'job_replacement': {'keywords': [], 'count': 0},
        'skill_requirements': {'keywords': [], 'count': 0},
        'career_development': {'keywords': [], 'count': 0},
        'ai_tools': {'keywords': [], 'count': 0},
        'industry_impact': {'keywords': [], 'count': 0},
        'emotional_response': {'keywords': [], 'count': 0}
    }

    if language == 'en':
        topics['job_replacement']['keywords'] = ['replace', 'replacement', 'obsolete', 'automate', 'automation', 'layoff', 'unemployed']
        topics['skill_requirements']['keywords'] = ['skill', 'skills', 'learn', 'learning', 'adapt', 'knowledge', 'experience']
        topics['career_development']['keywords'] = ['career', 'job', 'hire', 'hiring', 'junior', 'senior', 'entry', 'promotion']
        topics['ai_tools']['keywords'] = ['chatgpt', 'gpt', 'copilot', 'claude', 'cursor', 'tool', 'assistant', 'llm']
        topics['industry_impact']['keywords'] = ['industry', 'market', 'company', 'tech', 'software', 'developer', 'programmer']
        topics['emotional_response']['keywords'] = ['worry', 'fear', 'concern', 'hope', 'optimistic', 'pessimistic', 'anxious']
    else:
        topics['job_replacement']['keywords'] = ['取代', '替代', '淘汰', '自动化', '裁员', '失业']
        topics['skill_requirements']['keywords'] = ['技能', '学习', '适应', '知识', '经验', '能力']
        topics['career_development']['keywords'] = ['职业', '工作', '招聘', '初级', '高级', '晋升', '发展']
        topics['ai_tools']['keywords'] = ['chatgpt', 'gpt', 'copilot', 'claude', '工具', '助手', '大模型']
        topics['industry_impact']['keywords'] = ['行业', '市场', '公司', '技术', '软件', '开发', '程序员']
        topics['emotional_response']['keywords'] = ['担心', '焦虑', '恐惧', '希望', '乐观', '悲观']

    for text in texts:
        text_lower = text.lower()
        for topic, data in topics.items():
            for keyword in data['keywords']:
                if keyword in text_lower:
                    data['count'] += 1
                    break

    return topics


def main():
    processed_dir = Path("data/processed")
    analysis_dir = Path("data/analysis")
    analysis_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("文本分析 - 关键词提取与情感分析")
    print("=" * 60)

    # 加载数据
    print("\n[1/5] 加载数据...")
    with open(processed_dir / "merged_posts.json", 'r', encoding='utf-8') as f:
        posts = json.load(f)

    with open(processed_dir / "all_comments.json", 'r', encoding='utf-8') as f:
        comments = json.load(f)

    print(f"  ✓ 加载 {len(posts)} 个帖子, {len(comments)} 条评论")

    # 分离中英文内容
    print("\n[2/5] 分离中英文内容...")
    en_texts = []
    zh_texts = []

    for post in posts:
        text = f"{post.get('title', '')} {post.get('content', '')}"
        if post.get('language') == 'zh' or is_chinese(text):
            zh_texts.append(text)
        else:
            en_texts.append(text)

    for comment in comments:
        text = comment.get('content', '')
        if comment.get('platform') == 'v2ex' or is_chinese(text):
            zh_texts.append(text)
        else:
            en_texts.append(text)

    print(f"  ✓ 英文文本: {len(en_texts)} 条")
    print(f"  ✓ 中文文本: {len(zh_texts)} 条")

    # 关键词提取
    print("\n[3/5] 提取关键词...")
    en_keywords = extract_keywords(en_texts, 'en', 100)
    zh_keywords = extract_keywords(zh_texts, 'zh', 100)

    print(f"  ✓ 英文关键词 Top 10: {[kw[0] for kw in en_keywords[:10]]}")
    print(f"  ✓ 中文关键词 Top 10: {[kw[0] for kw in zh_keywords[:10]]}")

    # 情感分析
    print("\n[4/5] 情感分析...")
    en_sentiments = [analyze_sentiment(text, 'en') for text in en_texts]
    zh_sentiments = [analyze_sentiment(text, 'zh') for text in zh_texts]

    # 统计情感分布
    en_sentiment_dist = Counter([s['label'] for s in en_sentiments])
    zh_sentiment_dist = Counter([s['label'] for s in zh_sentiments])

    en_avg_score = sum(s['score'] for s in en_sentiments) / len(en_sentiments) if en_sentiments else 0
    zh_avg_score = sum(s['score'] for s in zh_sentiments) / len(zh_sentiments) if zh_sentiments else 0

    print(f"  ✓ 英文情感分布: {dict(en_sentiment_dist)}")
    print(f"    平均情感得分: {en_avg_score:.3f}")
    print(f"  ✓ 中文情感分布: {dict(zh_sentiment_dist)}")
    print(f"    平均情感得分: {zh_avg_score:.3f}")

    # 主题分析
    print("\n[5/5] 主题分析...")
    en_topics = extract_topics(en_texts, 'en')
    zh_topics = extract_topics(zh_texts, 'zh')

    print("  ✓ 英文主题分布:")
    for topic, data in en_topics.items():
        print(f"    - {topic}: {data['count']}")

    print("  ✓ 中文主题分布:")
    for topic, data in zh_topics.items():
        print(f"    - {topic}: {data['count']}")

    # 时间趋势分析
    print("\n[附加] 时间趋势分析...")
    time_sentiment = defaultdict(list)
    for post in posts:
        date_str = post.get('created_at', '')
        if date_str:
            year = date_str[:4]
            lang = 'zh' if post.get('language') == 'zh' else 'en'
            text = f"{post.get('title', '')} {post.get('content', '')}"
            sentiment = analyze_sentiment(text, lang)
            time_sentiment[year].append(sentiment['score'])

    time_trend = {}
    for year, scores in sorted(time_sentiment.items()):
        avg_score = sum(scores) / len(scores) if scores else 0
        time_trend[year] = {
            'count': len(scores),
            'avg_sentiment': round(avg_score, 3)
        }
        print(f"  {year}: {len(scores)} 帖子, 平均情感 {avg_score:.3f}")

    # 保存分析结果
    print("\n保存分析结果...")

    analysis_results = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_texts': len(en_texts) + len(zh_texts),
            'english_texts': len(en_texts),
            'chinese_texts': len(zh_texts)
        },
        'keywords': {
            'english': [{'word': kw[0], 'count': kw[1]} for kw in en_keywords],
            'chinese': [{'word': kw[0], 'count': kw[1]} for kw in zh_keywords]
        },
        'sentiment': {
            'english': {
                'distribution': dict(en_sentiment_dist),
                'average_score': round(en_avg_score, 3)
            },
            'chinese': {
                'distribution': dict(zh_sentiment_dist),
                'average_score': round(zh_avg_score, 3)
            }
        },
        'topics': {
            'english': {k: {'count': v['count']} for k, v in en_topics.items()},
            'chinese': {k: {'count': v['count']} for k, v in zh_topics.items()}
        },
        'time_trend': time_trend
    }

    with open(analysis_dir / "text_analysis_results.json", 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 分析结果: {analysis_dir / 'text_analysis_results.json'}")

    # 保存关键词详情（用于词云）
    with open(analysis_dir / "keywords_for_wordcloud.json", 'w', encoding='utf-8') as f:
        json.dump({
            'english': dict(en_keywords),
            'chinese': dict(zh_keywords)
        }, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 词云数据: {analysis_dir / 'keywords_for_wordcloud.json'}")

    print("\n" + "=" * 60)
    print("✅ 文本分析完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
