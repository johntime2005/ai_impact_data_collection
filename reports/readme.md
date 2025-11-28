# AI对IT行业就业影响数据分析项目

## 项目说明 (README)

---

### 项目概述

本项目旨在分析大模型（LLM）对IT行业就业岗位市场和职业技能的影响。通过收集Reddit和V2EX两大技术社区的讨论数据，运用文本分析和情感分析方法，深入探讨技术从业者对AI冲击的态度、认知和应对策略。

### 研究问题

1. IT从业者如何看待AI对其职业的影响？
2. 中英文技术社区在此问题上有何差异？
3. 从业者的态度随时间如何演变？
4. 哪些话题最受关注？

---

### 项目结构

```
ai_impact_data_collection/
├── data/
│   ├── raw/                          # 原始数据
│   │   ├── reddit_post_*.json        # Reddit帖子数据
│   │   ├── reddit_posts_fixed.json   # 修复后的Reddit数据
│   │   └── v2ex_ai_impact_posts.json # V2EX帖子数据
│   ├── processed/                    # 处理后的数据
│   │   ├── merged_posts.json         # 合并后的帖子数据
│   │   ├── all_comments.json         # 所有评论数据
│   │   └── data_statistics.json      # 数据统计信息
│   ├── analysis/                     # 分析结果
│   │   ├── text_analysis_results.json
│   │   └── keywords_for_wordcloud.json
│   └── visualizations/               # 可视化图表
│       ├── platform_distribution.png
│       ├── year_distribution.png
│       ├── sentiment_analysis.png
│       ├── topic_distribution.png
│       ├── keyword_frequency.png
│       ├── time_trend.png
│       ├── overview_dashboard.png
│       └── keyword_cloud.png
├── scripts/                          # 分析脚本
│   ├── data_merge_and_clean_v3.py    # 数据合并清洗
│   ├── text_analysis.py              # 文本分析
│   ├── generate_visualizations.py    # 可视化生成
│   └── fix_reddit_json.py            # 数据修复
├── reports/                          # 报告文档
│   ├── analysis_report.md            # 分析报告(Markdown)
│   └── analysis_report.pdf           # 分析报告(PDF)
├── src/                              # 源代码模块
│   ├── scrapers/                     # 数据采集模块
│   ├── analytics/                    # 分析模块
│   └── models/                       # 数据模型
└── README.md                         # 项目说明
```

---

### 数据说明

#### 数据来源

| 平台 | 语言 | 数据类型 | 采集方式 |
|------|------|----------|----------|
| Reddit | 英文 | 帖子+评论 | API/Web抓取 |
| V2EX | 中文 | 帖子+评论 | Web抓取 |

#### 数据规模

- **总帖子数**: 24篇
- **总评论数**: 885条
- **时间范围**: 2022年12月 - 2025年11月
- **平台分布**: Reddit 10篇, V2EX 14篇

#### 数据筛选标准

1. 帖子主题与"AI对IT从业者就业影响"相关
2. 帖子需有一定讨论量
3. 数据覆盖ChatGPT发布后的时间周期

---

### 分析方法

#### 1. 数据预处理
- 数据清洗：移除特殊字符、统一编码
- 日期标准化：统一为YYYY-MM-DD格式
- 语言识别：区分中英文内容

#### 2. 关键词分析
- 分词处理（中英文分别处理）
- 停用词过滤
- 词频统计

#### 3. 情感分析
- 基于情感词典的分析方法
- 计算正面/负面/中性比例
- 统计平均情感得分

#### 4. 主题分析
- 预定义主题类别
- 关键词匹配分类
- 统计各主题分布

#### 5. 时间趋势分析
- 按年份统计帖子数量
- 追踪情感得分变化趋势

---

### 运行环境

#### 系统要求
- Python 3.10+
- Windows/Linux/macOS

#### 依赖包
```
matplotlib>=3.7.0
numpy>=1.24.0
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

---

### 使用说明

#### 1. 数据合并与清洗
```bash
python scripts/data_merge_and_clean_v3.py
```

#### 2. 文本分析
```bash
python scripts/text_analysis.py
```

#### 3. 生成可视化图表
```bash
python scripts/generate_visualizations.py
```

---

### 主要发现

1. **情感趋势**: 从业者对AI的态度从2022年的强烈负面逐渐趋于理性
2. **区域差异**: 中文社区焦虑程度明显高于英文社区
3. **技能共识**: 持续学习被普遍认为是应对AI冲击的关键
4. **分层影响**: 初级岗位被认为受冲击较大，高级岗位相对安全

---

### 可视化说明

| 图表文件 | 说明 |
|----------|------|
| platform_distribution.png | 数据平台分布饼图 |
| year_distribution.png | 帖子年份分布柱状图 |
| sentiment_analysis.png | 中英文情感分布对比图 |
| topic_distribution.png | 主题分布横向条形图 |
| keyword_frequency.png | 高频关键词Top20图 |
| time_trend.png | 情感趋势时间线图 |
| overview_dashboard.png | 综合数据仪表板 |
| keyword_cloud.png | 关键词气泡云图 |

---

### 报告文件

- `reports/analysis_report.md` - Markdown格式完整分析报告
- `reports/analysis_report.pdf` - PDF格式报告（打印版）

报告包含：
- 研究背景与方法
- 数据统计概览
- 关键词分析
- 情感分析
- 主题分析
- 时间趋势分析
- 中英文社区对比
- 结论与建议

---

### 数据格式说明

#### 帖子数据格式 (merged_posts.json)
```json
{
  "id": "reddit_12345",
  "platform": "reddit",
  "title": "帖子标题",
  "content": "帖子内容",
  "author": "作者用户名",
  "url": "原始链接",
  "created_at": "2024-01-01",
  "comment_count": 100,
  "comments": [...],
  "language": "en"
}
```

#### 评论数据格式 (all_comments.json)
```json
{
  "author": "评论者用户名",
  "content": "评论内容",
  "upvotes": 50,
  "created_at": "2024-01-01",
  "platform": "reddit",
  "post_id": "reddit_12345",
  "post_title": "所属帖子标题"
}
```

---

### 局限性说明

1. 数据仅来自Reddit和V2EX，可能存在样本偏差
2. 情感分析基于词典方法，准确度有限
3. 无法区分专业从业者和非专业人士的观点
4. 部分评论可能包含讽刺或反语，影响情感判断

---

### 版权声明

本项目仅供学术研究使用。数据来源于公开社交媒体平台，仅用于非商业性分析研究。

---

### 联系方式

如有问题或建议，请联系研究小组。

---

*文档更新时间: 2025年11月28日*
