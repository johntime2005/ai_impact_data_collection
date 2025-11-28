"""
URL发现器 - 自动发现和收集相关讨论的URL

这个模块需要AI助手协助运行，因为需要调用搜索工具
"""
from typing import List, Dict, Optional
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
import sys
import os
from loguru import logger

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_search.smart_searcher import SmartSearcher, SearchResult
from utils.file_handler import save_json


class URLDiscoverer:
    """URL发现器 - AI辅助搜索和收集"""

    def __init__(self, use_perplexity: bool = False, perplexity_api_key: Optional[str] = None):
        self.searcher = SmartSearcher(use_perplexity, perplexity_api_key)
        self.discovered_urls = []

    def discover_urls_interactive(self) -> List[Dict]:
        """
        交互式URL发现

        这个方法会引导AI助手执行搜索并收集结果

        Returns:
            发现的URL列表
        """
        logger.info("=" * 60)
        logger.info("开始AI辅助URL发现流程")
        logger.info("=" * 60)

        # 搜索关键词列表
        search_queries = [
            # 知乎 - 按时间段和主题
            "site:zhihu.com ChatGPT 程序员 2023",
            "site:zhihu.com AI 失业 开发者 2024",
            "site:zhihu.com 大模型 技能 IT 2025",
            "site:zhihu.com GPT 就业 岗位",
            "site:zhihu.com 人工智能 编程 影响",

            # V2EX
            "site:v2ex.com ChatGPT programmer job",
            "site:v2ex.com AI developer career",
            "site:v2ex.com 大模型 程序员",
            "site:v2ex.com GPT 技能 学习",
        ]

        logger.info(f"将执行 {len(search_queries)} 个搜索查询")
        logger.info("请AI助手依次执行这些搜索...")

        # 这里返回搜索查询列表，让AI助手执行
        return {
            'search_queries': search_queries,
            'instructions': self._generate_instructions(),
            'expected_count': 18
        }

    def _generate_instructions(self) -> str:
        """生成给AI助手的指令"""
        return """
## AI助手执行指令

请按照以下步骤帮我发现相关URL：

### 第1步：执行搜索
对于上述每个搜索查询，使用 WebSearch 工具进行搜索。

### 第2步：筛选结果
从搜索结果中筛选出：
1. 来自知乎（zhihu.com）或V2EX（v2ex.com）的链接
2. 标题明确涉及"大模型/AI对IT岗位或技能影响"的讨论
3. 看起来有较多讨论（点赞、回复多）的帖子

### 第3步：收集信息
对于每个候选URL，收集：
- url: 完整URL
- title: 标题
- platform: 平台（zhihu/v2ex）
- snippet: 简短描述
- estimated_date: 估计发布时间（从搜索结果推断）

### 第4步：生成配置
将收集到的URL整理成JSON格式，可以直接用于配置文件。

目标：找到至少18个符合条件的URL
"""

    def analyze_search_result(self, search_result_text: str) -> List[Dict]:
        """
        分析搜索结果文本，提取URL和相关信息

        Args:
            search_result_text: 搜索结果的原始文本

        Returns:
            提取的URL信息列表
        """
        # 这个方法用于解析AI助手提供的搜索结果
        logger.info("分析搜索结果...")

        # 提取URL
        import re
        urls = re.findall(r'https?://(?:www\.)?(?:zhihu\.com|v2ex\.com)[^\s<>"{}|\\^`\[\]]+', search_result_text)

        discovered = []
        for url in urls:
            platform = 'zhihu' if 'zhihu.com' in url else 'v2ex'
            discovered.append({
                'url': url,
                'platform': platform,
                'discovered_at': datetime.now().isoformat(),
                'needs_manual_check': True
            })

        logger.info(f"发现 {len(discovered)} 个潜在URL")
        return discovered

    def save_discoveries(self, urls: List[Dict], output_path: Path):
        """
        保存发现的URL

        Args:
            urls: URL列表
            output_path: 输出文件路径
        """
        data = {
            'discovered_at': datetime.now().isoformat(),
            'total_count': len(urls),
            'zhihu_count': sum(1 for u in urls if u.get('platform') == 'zhihu'),
            'v2ex_count': sum(1 for u in urls if u.get('platform') == 'v2ex'),
            'urls': urls,
            'note': '这些URL需要人工复核，确认相关性和评论数量后，添加到 config/target_urls.json'
        }

        save_json(data, output_path, pretty=True)
        logger.success(f"发现结果已保存: {output_path}")

    def generate_target_config_template(self, urls: List[Dict], output_path: Path):
        """
        生成目标配置文件模板

        Args:
            urls: URL列表
            output_path: 输出路径
        """
        zhihu_posts = []
        v2ex_posts = []

        for url_info in urls:
            template = {
                'url': url_info['url'],
                'title': url_info.get('title', '需要填写'),
                'date': url_info.get('estimated_date', '需要填写'),
                'relevance_note': '需要填写相关性说明',
                'manual_checked': False  # 需要人工确认后改为True
            }

            if url_info['platform'] == 'zhihu':
                zhihu_posts.append(template)
            else:
                v2ex_posts.append(template)

        config = {
            'comment': '自动发现的URL，需要人工复核',
            'instructions': [
                '1. 访问每个URL，确认是否相关',
                '2. 检查评论数是否>=100',
                '3. 填写title、date和relevance_note',
                '4. 确认后将manual_checked改为true',
                '5. 确保总数>=18个已确认的帖子'
            ],
            'zhihu_posts': zhihu_posts,
            'v2ex_posts': v2ex_posts,
            'stats': {
                'zhihu_count': len(zhihu_posts),
                'v2ex_count': len(v2ex_posts),
                'total': len(urls),
                'checked': 0
            }
        }

        save_json(config, output_path, pretty=True)
        logger.success(f"配置模板已生成: {output_path}")
