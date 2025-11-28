# Notebooks 目录

本目录用于存放 Jupyter Notebooks，用于交互式数据探索和实验。

## 📝 推荐的 Notebook 组织方式

使用数字前缀来标记分析流程的顺序：

- `01_exploratory_analysis.ipynb` - 探索性数据分析
- `02_data_quality_check.ipynb` - 数据质量检查
- `03_sentiment_analysis.ipynb` - 情感分析
- `04_topic_modeling.ipynb` - 主题建模
- `05_visualization.ipynb` - 数据可视化

## 🎯 使用场景

- **初步探索**: 快速查看数据分布、统计特征
- **实验验证**: 测试不同的分析方法和参数
- **可视化呈现**: 生成图表和交互式可视化
- **文档记录**: 保留分析思路和发现

## 💡 最佳实践

1. **清晰命名**: 使用描述性的文件名
2. **添加注释**: 使用 Markdown 单元格解释分析思路
3. **模块化**: 将可复用代码提取到 `analytics/` 模块
4. **版本控制**: 定期清理输出，避免提交大文件

## 🔧 环境配置

确保已安装必要的依赖：

```bash
# 使用 pixi
pixi install jupyter

# 或使用 pip
pip install jupyter pandas matplotlib seaborn
```

启动 Jupyter：

```bash
jupyter notebook
```

## 📂 相关目录

- `../analytics/` - 可复用的分析模块
- `../data/` - 数据文件
- `../outputs/` - 分析结果输出
