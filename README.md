# 大模型对IT行业影响 - 数据采集与分析系统

> 📊 基于社区讨论数据分析大模型（ChatGPT等）对IT行业就业岗位和职业技能的影响

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Rust-Powered](https://img.shields.io/badge/powered%20by-Rust-orange.svg)](https://www.rust-lang.org/)

## ✨ 特性

- 🦀 **高性能**: 使用 Rust 加速库（Polars、orjson、Pydantic v2）
- 🤖 **AI智能搜索**: 自动发现相关讨论，减少90%人工搜索工作量
- 🔍 **多平台采集**: 支持知乎、V2EX等主流技术社区
- 📈 **完整分析**: 数据清洗、质量分析、文本分析、报告生成
- 🎯 **符合作业要求**: ≥18个主贴，每个≥100条评论
- 📝 **可复现**: 完整的代码和配置，支持复现分析过程

## 📁 项目结构

```
ai_impact_data_collection/
├── config/                    # 配置文件
│   ├── config.py              # 基础配置
│   └── target_urls.json       # 目标URL列表
├── ai_search/                 # 🆕 AI智能搜索模块
│   ├── smart_searcher.py      # 智能搜索器（支持Perplexity）
│   ├── url_discoverer.py      # URL自动发现
│   └── relevance_evaluator.py # 相关性评估
├── models/                    # 数据模型（Pydantic）
│   ├── post.py                # 帖子模型
│   └── comment.py             # 评论模型
├── scrapers/                  # 爬虫模块
│   ├── base_scraper.py        # 基础爬虫类
│   ├── zhihu_scraper.py       # 知乎爬虫
│   └── v2ex_scraper.py        # V2EX爬虫
├── utils/                     # 工具函数
│   ├── logger.py              # 日志配置
│   ├── file_handler.py        # 文件IO（orjson加速）
│   └── helpers.py             # 辅助函数
├── analytics/                 # 数据分析
│   ├── data_cleaner.py        # 数据清洗（Polars加速）
│   ├── quality_analyzer.py    # 质量分析
│   ├── text_analyzer.py       # 文本分析
│   └── report_generator.py    # 报告生成
├── data/                      # 数据目录
│   ├── raw/                   # 原始数据
│   ├── processed/             # 处理后数据
│   ├── reports/               # 分析报告
│   └── discovered_urls.json   # 🆕 AI发现的URL
├── main.py                    # 主程序入口
├── ai_search_helper.py        # 🆕 AI搜索助手
├── pixi.toml                  # Pixi依赖配置
└── README.md                  # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

使用 Pixi（推荐）:

```bash
cd ai_impact_data_collection

# 安装依赖
pixi install

# 激活环境
pixi shell
```

或使用 pip:

```bash
cd ai_impact_data_collection
pip install -r requirements.txt
```

### 2. 🤖 使用AI智能搜索（推荐！大幅减少工作量）

**✨ 新功能**：浮浮酱已经帮主人搜索了16+个高质量讨论！

```bash
# 查看已发现的URL
cat data/discovered_urls.json
```

浮浮酱已经通过AI搜索找到了以下高质量讨论：

#### 知乎热门讨论（10个）:
- "OpenAI 的超级对话模型 ChatGPT 会导致程序员大规模失业吗？" - 近百万浏览
- "ChatGPT的出现会不会导致底层程序员失业？"
- "程序员如何转行到AI大模型领域？"
- "AI大模型求职真相：我们扒了数百份招聘JD"
- 还有更多...

#### V2EX程序员社区（6个）:
- "人工智能（AI）井喷式发展下，未来'程序员'这个职业会不存在吗？"
- "程序员 10 年，想转做 AI 应用方向"
- "35 岁+程序员， Gap 10 个月后成功再就业"
- 还有更多...

**下一步**（只需几分钟）：
```bash
# 1. 复核评论数量（浮浮酱已经帮你筛选好了相关性）
# 打开 data/discovered_urls.json 中的每个URL
# 确认评论数 >= 100

# 2. 填写准确信息并复制到配置文件
cp data/discovered_urls.json config/target_urls.json

# 3. 编辑 config/target_urls.json
# 将确认的URL的 manual_checked 改为 true
```

#### 可选：使用Perplexity Sonar进一步增强搜索

如果你有Perplexity API密钥（Sonar模型擅长实时搜索）：

```bash
python ai_search_helper.py discover --perplexity --api-key YOUR_KEY
python ai_search_helper.py review
```

---

### 2.1 手动配置目标URL（传统方式）

⚠️ **如果不使用AI搜索**：需要手动搜索并筛选相关讨论

编辑 `config/target_urls.json`:

```json
{
  "zhihu_posts": [
    {
      "url": "https://www.zhihu.com/question/xxxxxx",
      "title": "ChatGPT会让程序员失业吗？",
      "date": "2023-01-15",
      "relevance_note": "讨论AI对程序员岗位的影响",
      "manual_checked": true
    }
  ],
  "v2ex_posts": [
    {
      "url": "https://www.v2ex.com/t/xxxxxx",
      "title": "大模型时代，我们该学什么技能？",
      "date": "2023-06-20",
      "relevance_note": "讨论技能转型",
      "manual_checked": true
    }
  ]
}
```

**搜索建议**:
- **知乎**: 搜索 "ChatGPT 程序员"、"AI 失业"、"大模型 开发者"
- **V2EX**: 在 /go/programmer、/go/career 板块搜索

**筛选标准**:
1. 讨论内容明确涉及"大模型对IT岗位/技能的影响"
2. 评论数 ≥ 100条
3. 时间跨度覆盖 2022.12 - 2025.11
4. 需要≥18个主贴

### 3. 运行程序

```bash
# 查看帮助
python main.py -h

# 执行完整流程（推荐）
python main.py full

# 或分步执行
python main.py scrape      # 仅采集数据
python main.py analyze     # 仅分析数据
```

### 4. 查看结果

- **原始数据**: `data/raw/posts_*.json`
- **清洗后数据**: `data/processed/cleaned_*.json`
- **分析报告**: `data/reports/report_*.md`
- **日志文件**: `logs/app_*.log`

## 📊 数据采集要求

| 要求 | 标准 | 本系统 |
|------|------|--------|
| 最少主贴数 | ≥18 | ✅ 支持 |
| 每帖最少评论数 | ≥100 | ✅ 自动验证 |
| 时间跨度 | 2022.12-2025.11 | ✅ 支持 |
| 人工筛选 | 需要 | ✅ 配置文件标记 |
| 数据可复现 | 需要 | ✅ 完整代码和配置 |

## 🔧 配置说明

### 爬虫配置 (`config/config.py`)

```python
# 请求配置
REQUEST_TIMEOUT = 30          # 请求超时（秒）
REQUEST_DELAY_MIN = 2         # 最小请求间隔（秒）
REQUEST_DELAY_MAX = 5         # 最大请求间隔（秒）
MAX_RETRIES = 3               # 最大重试次数

# 数据质量要求
MIN_COMMENTS_PER_POST = 100   # 每帖最少评论数
MIN_POSTS_REQUIRED = 18       # 最少主贴数
```

### 知乎Cookie配置（可选）

知乎需要登录才能看到完整评论。如需采集完整数据：

1. 在浏览器登录知乎
2. F12 -> Network -> 复制 Cookie
3. 修改爬虫初始化：

```python
# scrapers/zhihu_scraper.py
scraper = ZhihuScraper(cookie="your_cookie_here")
```

## 📈 数据分析功能

### 1. 数据清洗
- 去除重复帖子
- 清理HTML标签和多余空白
- 过滤无效数据
- 使用 **Polars**（Rust实现）高性能处理

### 2. 质量分析
- 基础统计（帖子数、评论数）
- 平台分布
- 时间分布
- 质量评分（0-100）

### 3. 文本分析
- 关键词覆盖率
- 高频词汇统计
- 简单情感分析

### 4. 报告生成
- Markdown格式
- 包含图表和统计数据
- 提供后续分析建议

## 🎯 作业提交清单

按照作业要求，提交文件应包括：

```
安卓_数据分析.zip               # 压缩包（替换"安卓"为你的组名）
├── 安卓_报告.pdf               # 8-25页的分析报告
├── code/                       # 代码目录
│   └── ai_impact_data_collection/
│       ├── config/
│       ├── scrapers/
│       ├── analytics/
│       ├── main.py
│       └── ...
└── data/                       # 数据目录（可选）
    ├── raw/                    # 原始数据
    └── processed/              # 处理后数据
```

### 报告生成

系统会自动生成Markdown格式的报告 (`data/reports/report_*.md`)，你需要：

1. 将Markdown转换为PDF（推荐工具：Typora、Pandoc）
2. 补充图表和可视化分析
3. 添加结论和讨论章节
4. 确保篇幅在8-25页

## 🛠️ 技术栈

### 高性能Rust库

| Python库 | Rust加速 | 用途 |
|----------|----------|------|
| Polars | ✅ | 数据处理（比pandas快数倍） |
| orjson | ✅ | JSON序列化（比标准库快5-10倍） |
| Pydantic v2 | ✅ | 数据验证（使用pydantic-core） |
| httpx | 部分 | HTTP客户端 |
| ruff | ✅ | 代码检查和格式化 |

### 核心库

- **爬虫**: requests, BeautifulSoup4, lxml
- **日志**: loguru
- **数据分析**: polars, numpy
- **时间处理**: python-dateutil

## ⚠️ 注意事项

### 1. 反爬虫机制
- 知乎反爬较强，建议配置Cookie
- V2EX相对宽松，但仍需控制频率
- **请求间隔已自动设置2-5秒**

### 2. 数据质量
- 必须人工筛选相关讨论
- 确保每个帖子评论数≥100
- 时间跨度尽量均匀分布

### 3. 法律合规
- 仅用于学术研究
- 遵守平台robots.txt
- 不进行商业用途

## 🐛 常见问题

### Q: 知乎采集不到完整评论？
A: 需要配置Cookie。参见"知乎Cookie配置"章节。

### Q: Polars安装失败？
A: 使用pixi安装，或手动安装：`pip install polars`

### Q: 如何查找相关讨论？
A: 在知乎、V2EX搜索关键词，人工筛选后添加到配置文件。

### Q: 报告如何转换为PDF？
A: 使用Typora、Pandoc或在线工具转换Markdown。

## 📝 开发日志

- **2025-11**: 项目创建，完成基础框架
- 使用Rust加速库提升性能
- 实现知乎和V2EX爬虫
- 完成数据清洗和质量分析
- 添加自动化报告生成

## 📄 License

MIT License - 仅用于学术研究

## 👥 贡献

如果你有改进建议：
1. Fork本项目
2. 创建新分支 (`git checkout -b feature/improvement`)
3. 提交更改 (`git commit -am 'Add improvement'`)
4. 推送到分支 (`git push origin feature/improvement`)
5. 创建Pull Request

---

**祝你的数据分析作业顺利完成！** 🎉

如有问题，请检查 `logs/` 目录下的日志文件。
