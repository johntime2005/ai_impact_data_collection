# AI对IT行业就业影响数据分析项目

## 项目概述

本项目通过收集和分析Reddit、V2EX技术社区关于"大模型对IT行业就业影响"的讨论数据，研究技术从业者对AI冲击的态度变化和认知演进。

## 数据规模

- **总帖子数**: 24篇
- **总评论数**: 885条  
- **时间跨度**: 2022年12月 - 2025年11月
- **数据来源**: Reddit (英文), V2EX (中文)

## 项目结构

```
ai_impact_data_collection/
├── data/
│   ├── raw/                    # 原始采集数据
│   ├── processed/              # 清洗后数据
│   ├── analysis/               # 分析结果
│   └── visualizations/         # 可视化图表
├── scripts/                    # 分析脚本
├── reports/                    # 分析报告
│   ├── analysis_report.md      # 完整分析报告
│   └── readme.md               # 项目说明文档
├── src/                        # 源代码模块
└── requirements.txt            # 依赖包
```

## 核心发现

1. **情感演变**: 从2022年强烈负面(-1.0)逐渐缓和至2025年(-0.4)
2. **区域差异**: 中文社区焦虑程度明显高于英文社区
3. **技能共识**: 持续学习被认为是应对AI冲击的关键
4. **分层影响**: 初级岗位受冲击较大，高级岗位相对安全

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 数据合并清洗
python scripts/data_merge_and_clean_v3.py

# 文本分析
python scripts/text_analysis.py

# 生成可视化
python scripts/generate_visualizations.py
```

## 报告文件

- `reports/analysis_report.md` - 完整分析报告 (约15页)
- `reports/readme.md` - 项目详细说明文档

## 可视化图表

- 平台分布图、年份分布图
- 情感分析图、主题分布图  
- 关键词频率图、时间趋势图
- 综合仪表板、关键词云图

---

*项目完成时间: 2025年11月28日*
