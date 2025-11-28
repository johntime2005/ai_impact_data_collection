"""
智能搜索器 - 使用AI搜索引擎自动发现相关讨论

支持多种搜索引擎：
1. 内置WebSearch (优先)
2. DuckDuckGo (mcp__open-websearch)
3. Perplexity Sonar (如果配置了API密钥)
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import re
from loguru import logger


@dataclass
class SearchResult:
    """搜索结果"""
    url: str
    title: str
    snippet: str
    platform: str
    estimated_relevance: float  # 0.0-1.0
    search_engine: str


class SmartSearcher:
    """智能搜索器"""

    def __init__(self, use_perplexity: bool = False, perplexity_api_key: Optional[str] = None):
        """
        初始化智能搜索器

        Args:
            use_perplexity: 是否使用Perplexity Sonar
            perplexity_api_key: Perplexity API密钥
        """
        self.use_perplexity = use_perplexity
        self.perplexity_api_key = perplexity_api_key

        # 搜索查询模板
        self.search_queries = [
            # 知乎相关查询
            'site:zhihu.com ChatGPT 程序员 失业',
            'site:zhihu.com AI 大模型 IT 岗位',
            'site:zhihu.com 人工智能 开发者 就业',
            'site:zhihu.com GPT 技术 职业',
            'site:zhihu.com 大语言模型 程序员 影响',

            # V2EX相关查询
            'site:v2ex.com ChatGPT programmer',
            'site:v2ex.com AI 程序员 就业',
            'site:v2ex.com 大模型 开发',
            'site:v2ex.com GPT 技能',

            # 通用查询
            'ChatGPT 程序员 失业 讨论',
            'AI 大模型 IT行业 影响',
            '人工智能 开发者 技能',
        ]

        logger.info(f"智能搜索器初始化完成 (Perplexity: {use_perplexity})")

    def search_with_builtin(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """
        使用内置搜索引擎搜索

        注意：这个方法需要在Claude Code环境中由AI自己调用搜索工具

        Args:
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        logger.info(f"执行搜索: {query}")

        # 提示：实际使用时，这个方法会被AI助手调用WebSearch工具
        # 这里提供一个框架，实际实现在主程序中通过AI交互完成

        results = []
        logger.info("需要AI助手调用WebSearch工具来执行此搜索")

        return results

    def search_with_duckduckgo(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """
        使用DuckDuckGo搜索（通过MCP）

        Args:
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        # 类似地，需要调用 mcp__open-websearch__search
        logger.info(f"DuckDuckGo搜索: {query}")
        return []

    def search_with_perplexity(self, query: str) -> List[SearchResult]:
        """
        使用Perplexity Sonar搜索

        Args:
            query: 搜索查询

        Returns:
            搜索结果列表
        """
        if not self.use_perplexity or not self.perplexity_api_key:
            logger.warning("Perplexity未配置")
            return []

        try:
            import httpx

            # Perplexity Sonar API调用
            # 文档: https://docs.perplexity.ai/
            headers = {
                'Authorization': f'Bearer {self.perplexity_api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': 'sonar-small-online',  # 或 sonar-medium-online
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一个专业的信息检索助手，帮助找到关于大模型对IT行业影响的相关讨论。'
                    },
                    {
                        'role': 'user',
                        'content': f'搜索并列出关于"{query}"的中文技术社区讨论，重点关注知乎和V2EX平台。'
                    }
                ],
                'max_tokens': 1000,
                'temperature': 0.2,
                'return_citations': True,
                'search_domain_filter': ['zhihu.com', 'v2ex.com']
            }

            response = httpx.post(
                'https://api.perplexity.ai/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                # 解析Perplexity返回的结果和引用
                citations = result.get('citations', [])

                search_results = []
                for citation in citations:
                    search_results.append(SearchResult(
                        url=citation,
                        title='',  # 需要进一步获取
                        snippet='',
                        platform=self._detect_platform(citation),
                        estimated_relevance=0.8,  # Sonar返回的通常相关性高
                        search_engine='perplexity_sonar'
                    ))

                logger.success(f"Perplexity搜索成功: {len(search_results)} 个结果")
                return search_results
            else:
                logger.error(f"Perplexity API错误: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Perplexity搜索失败: {e}")
            return []

    def _detect_platform(self, url: str) -> str:
        """检测URL所属平台"""
        if 'zhihu.com' in url:
            return 'zhihu'
        elif 'v2ex.com' in url:
            return 'v2ex'
        elif 'xiaohongshu.com' in url:
            return 'xiaohongshu'
        elif 'bilibili.com' in url:
            return 'bilibili'
        else:
            return 'unknown'

    def _extract_urls_from_text(self, text: str) -> List[str]:
        """从文本中提取URL"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        return urls

    def filter_by_platform(self, results: List[SearchResult], platforms: List[str]) -> List[SearchResult]:
        """按平台过滤结果"""
        return [r for r in results if r.platform in platforms]

    def filter_by_relevance(self, results: List[SearchResult], min_relevance: float = 0.5) -> List[SearchResult]:
        """按相关性过滤结果"""
        return [r for r in results if r.estimated_relevance >= min_relevance]

    def deduplicate(self, results: List[SearchResult]) -> List[SearchResult]:
        """去重"""
        seen_urls = set()
        unique_results = []

        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)

        return unique_results
