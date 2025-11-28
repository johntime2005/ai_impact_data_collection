#!/usr/bin/env python3
"""
使用Perplexity API搜索符合要求的讨论URL

用法：
    export PERPLEXITY_API_KEY="your-api-key"
    python perplexity_search.py

或者：
    python perplexity_search.py --api-key "your-api-key"
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import requests
from datetime import datetime


class PerplexityURLSearcher:
    """使用Perplexity API搜索符合要求的讨论URL"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def search_urls(self, target_count: int = 20) -> Dict[str, List[Dict]]:
        """
        搜索符合要求的URL

        Args:
            target_count: 目标URL数量

        Returns:
            包含zhihu和v2ex URL列表的字典
        """
        print(f"\n🔍 开始使用Perplexity API搜索URL... 目标数量: {target_count}")

        # 构造搜索prompt
        prompt = self._build_search_prompt(target_count)

        # 调用API
        response = self._call_api(prompt)

        # 解析结果
        urls = self._parse_response(response)

        return urls

    def _build_search_prompt(self, count: int) -> str:
        """构造搜索prompt"""
        return f"""请帮我在知乎和V2EX上找{count}个关于"ChatGPT/大模型/AI对IT行业影响"的热门讨论帖子。

要求：
1. 讨论主题：必须是关于AI/ChatGPT/大模型对IT从业者、程序员的影响（包括就业、技能需求、职业发展等）
2. 评论数量：每个帖子必须有≥100条回答/评论
3. 平台：知乎问题(zhihu.com/question/)或V2EX讨论帖(v2ex.com/t/)
4. 时效性：优先选择2023-2024年的讨论
5. 热度：选择讨论热度高、互动多的帖子

请直接给出URL列表，格式如下：
知乎：
- https://www.zhihu.com/question/xxxxx (标题：xxx，回答数：xxx)
- https://www.zhihu.com/question/xxxxx (标题：xxx，回答数：xxx)

V2EX：
- https://v2ex.com/t/xxxxx (标题：xxx，回复数：xxx)
- https://v2ex.com/t/xxxxx (标题：xxx，回复数：xxx)

请确保每个URL都是真实存在的，并且评论数≥100。"""

    def _call_api(self, prompt: str, model: str = "sonar-pro") -> str:
        """
        调用Perplexity API

        Args:
            prompt: 搜索prompt
            model: 使用的模型（sonar模型支持在线搜索）

        Returns:
            API响应内容
        """
        print(f"\n📡 正在调用Perplexity API (模型: {model})...")

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的中文互联网内容搜索助手，擅长在知乎、V2EX等平台上找到高质量的讨论帖子。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,  # 降低随机性，提高准确性
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            content = result['choices'][0]['message']['content']

            print(f"✅ API调用成功！响应长度: {len(content)} 字符")
            return content

        except requests.exceptions.RequestException as e:
            print(f"❌ API调用失败: {e}")
            if hasattr(e.response, 'text'):
                print(f"错误详情: {e.response.text}")
            raise

    def _parse_response(self, response: str) -> Dict[str, List[Dict]]:
        """
        解析API响应，提取URL

        Args:
            response: API响应内容

        Returns:
            包含zhihu和v2ex URL的字典
        """
        print("\n📝 解析API响应...")

        urls = {
            "zhihu": [],
            "v2ex": []
        }

        # 正则表达式提取知乎URL
        zhihu_pattern = r'https://www\.zhihu\.com/question/(\d+)'
        zhihu_matches = re.finditer(zhihu_pattern, response)

        for match in zhihu_matches:
            question_id = match.group(1)
            url = f"https://www.zhihu.com/question/{question_id}"

            # 尝试提取标题和评论数
            title, comment_count = self._extract_metadata(response, url)

            urls["zhihu"].append({
                "url": url,
                "question_id": question_id,
                "title": title,
                "estimated_comments": comment_count,
                "source": "perplexity_api",
                "search_date": datetime.now().isoformat()
            })

        # 正则表达式提取V2EX URL
        v2ex_pattern = r'https://(?:www\.)?v2ex\.com/t/(\d+)'
        v2ex_matches = re.finditer(v2ex_pattern, response)

        for match in v2ex_matches:
            topic_id = match.group(1)
            url = f"https://v2ex.com/t/{topic_id}"

            # 尝试提取标题和评论数
            title, comment_count = self._extract_metadata(response, url)

            urls["v2ex"].append({
                "url": url,
                "topic_id": topic_id,
                "title": title,
                "estimated_comments": comment_count,
                "source": "perplexity_api",
                "search_date": datetime.now().isoformat()
            })

        # 去重
        urls["zhihu"] = self._deduplicate_urls(urls["zhihu"], "question_id")
        urls["v2ex"] = self._deduplicate_urls(urls["v2ex"], "topic_id")

        print(f"✅ 找到 {len(urls['zhihu'])} 个知乎URL")
        print(f"✅ 找到 {len(urls['v2ex'])} 个V2EX URL")
        print(f"📊 总计: {len(urls['zhihu']) + len(urls['v2ex'])} 个URL")

        return urls

    def _extract_metadata(self, text: str, url: str) -> tuple[Optional[str], Optional[int]]:
        """从响应文本中提取URL的元数据"""
        # 尝试找到URL所在行
        for line in text.split('\n'):
            if url in line:
                # 提取标题
                title_match = re.search(r'标题[：:](.*?)(?:，|,|回答数|回复数|$)', line)
                title = title_match.group(1).strip() if title_match else None

                # 提取评论数
                count_match = re.search(r'(?:回答数|回复数)[：:](\d+)', line)
                comment_count = int(count_match.group(1)) if count_match else None

                return title, comment_count

        return None, None

    def _deduplicate_urls(self, url_list: List[Dict], id_key: str) -> List[Dict]:
        """根据ID去重"""
        seen_ids = set()
        unique_urls = []

        for url_info in url_list:
            url_id = url_info.get(id_key)
            if url_id and url_id not in seen_ids:
                seen_ids.add(url_id)
                unique_urls.append(url_info)

        return unique_urls

    def save_results(self, urls: Dict[str, List[Dict]], output_file: str = "data/perplexity_urls.json"):
        """保存搜索结果到JSON文件"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 添加统计信息
        result = {
            "search_date": datetime.now().isoformat(),
            "total_count": len(urls["zhihu"]) + len(urls["v2ex"]),
            "zhihu_count": len(urls["zhihu"]),
            "v2ex_count": len(urls["v2ex"]),
            "urls": urls
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n💾 结果已保存到: {output_path}")

    def display_results(self, urls: Dict[str, List[Dict]]):
        """显示搜索结果"""
        print("\n" + "="*60)
        print("🎯 搜索结果汇总")
        print("="*60)

        if urls["zhihu"]:
            print(f"\n📚 知乎 ({len(urls['zhihu'])}个):")
            for i, url_info in enumerate(urls["zhihu"], 1):
                title = url_info.get('title', '未知标题')
                count = url_info.get('estimated_comments', '?')
                print(f"  {i}. {url_info['url']}")
                print(f"     标题: {title}")
                print(f"     预估回答数: {count}")

        if urls["v2ex"]:
            print(f"\n💬 V2EX ({len(urls['v2ex'])}个):")
            for i, url_info in enumerate(urls["v2ex"], 1):
                title = url_info.get('title', '未知标题')
                count = url_info.get('estimated_comments', '?')
                print(f"  {i}. {url_info['url']}")
                print(f"     标题: {title}")
                print(f"     预估回复数: {count}")

        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="使用Perplexity API搜索符合要求的讨论URL"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Perplexity API Key（也可以通过环境变量PERPLEXITY_API_KEY设置）"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=20,
        help="目标URL数量（默认: 20）"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/perplexity_urls.json",
        help="输出文件路径（默认: data/perplexity_urls.json）"
    )

    args = parser.parse_args()

    # 获取API Key
    api_key = args.api_key or os.getenv("PERPLEXITY_API_KEY")

    if not api_key:
        print("❌ 错误: 未找到API Key！")
        print("\n请通过以下方式之一提供API Key:")
        print("  1. 设置环境变量: export PERPLEXITY_API_KEY='your-api-key'")
        print("  2. 使用命令行参数: --api-key 'your-api-key'")
        sys.exit(1)

    print("🚀 Perplexity URL 搜索工具")
    print("="*60)
    print(f"目标数量: {args.count}")
    print(f"输出文件: {args.output}")
    print("="*60)

    try:
        # 创建搜索器
        searcher = PerplexityURLSearcher(api_key)

        # 执行搜索
        urls = searcher.search_urls(target_count=args.count)

        # 显示结果
        searcher.display_results(urls)

        # 保存结果
        searcher.save_results(urls, args.output)

        print("\n✅ 搜索完成！")
        print(f"\n💡 下一步:")
        print(f"  1. 查看搜索结果: cat {args.output}")
        print(f"  2. 验证URL的真实评论数（可能需要）")
        print(f"  3. 将验证后的URL添加到 config/target_urls.json")

    except Exception as e:
        print(f"\n❌ 搜索失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
