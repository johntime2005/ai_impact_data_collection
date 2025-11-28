#!/usr/bin/env python3
"""
使用Perplexity API重新搜索V2EX高质量讨论URL

用法：
    export PERPLEXITY_API_KEY="your-api-key"
    python perplexity_search_v2ex.py
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


class PerplexityV2EXSearcher:
    """使用Perplexity API专门搜索V2EX符合要求的讨论URL"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def search_v2ex_urls(self, target_count: int = 20) -> List[Dict]:
        """
        多次搜索V2EX，收集足够的高质量URL

        Args:
            target_count: 目标URL数量

        Returns:
            V2EX URL列表
        """
        print(f"\n🔍 开始搜索V2EX讨论... 目标数量: {target_count}")

        all_urls = []

        # 多个搜索关键词，增加覆盖面
        search_queries = [
            "V2EX ChatGPT 程序员 失业 讨论 回复数超过100",
            "V2EX AI 大模型 IT 行业 影响 热门讨论 评论多",
            "V2EX GPT 码农 工作 技能 讨论帖 回复100以上",
            "V2EX 人工智能 开发者 就业 职业发展 热帖",
        ]

        for i, query in enumerate(search_queries, 1):
            print(f"\n{'='*60}")
            print(f"🔎 第{i}次搜索: {query}")
            print(f"{'='*60}")

            prompt = self._build_v2ex_prompt(query)
            response = self._call_api(prompt)
            urls = self._parse_v2ex_response(response)

            # 合并去重
            for url_info in urls:
                if not any(u['topic_id'] == url_info['topic_id'] for u in all_urls):
                    all_urls.append(url_info)

            print(f"✅ 本次找到 {len(urls)} 个新URL")
            print(f"📊 总计: {len(all_urls)} 个URL")

            if len(all_urls) >= target_count:
                print(f"\n🎉 已收集足够数量的URL!")
                break

        return all_urls[:target_count]

    def _build_v2ex_prompt(self, query: str) -> str:
        """构造V2EX专用搜索prompt"""
        return f"""请帮我在V2EX社区找15-20个关于"{query}"的热门讨论帖子。

**硬性要求（必须满足）：**
1. 平台：必须是 v2ex.com/t/ 开头的讨论帖URL
2. 回复数：每个帖子必须≥100条回复（这是最重要的！）
3. 主题：必须与AI/ChatGPT/大模型对IT从业者/程序员的影响相关
4. 时效性：优先2023-2024年的讨论

**请直接给出URL列表，格式如下：**
- https://v2ex.com/t/xxxxx (标题：xxx，回复数：xxx)
- https://v2ex.com/t/xxxxx (标题：xxx，回复数：xxx)

**重要提醒：**
- 只要V2EX的URL，不要知乎、GitHub等其他平台
- 回复数必须≥100，少于100的不要
- 确保URL真实存在"""

    def _call_api(self, prompt: str, model: str = "sonar-pro") -> str:
        """调用Perplexity API"""
        print(f"\n📡 正在调用Perplexity API...")

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是专业的V2EX社区内容搜索助手，擅长找到高质量、高互动的技术讨论帖子。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
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
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"错误详情: {e.response.text}")
            raise

    def _parse_v2ex_response(self, response: str) -> List[Dict]:
        """解析API响应，提取V2EX URL"""
        print("\n📝 解析API响应...")

        urls = []

        # 正则表达式提取V2EX URL
        v2ex_pattern = r'https://(?:www\.)?v2ex\.com/t/(\d+)'
        matches = re.finditer(v2ex_pattern, response)

        for match in matches:
            topic_id = match.group(1)
            url = f"https://v2ex.com/t/{topic_id}"

            # 尝试提取标题和回复数
            title, reply_count = self._extract_metadata(response, url)

            urls.append({
                "url": url,
                "topic_id": topic_id,
                "title": title,
                "estimated_replies": reply_count,
                "source": "perplexity_api_v2",
                "search_date": datetime.now().isoformat()
            })

        # 去重
        seen_ids = set()
        unique_urls = []
        for url_info in urls:
            if url_info['topic_id'] not in seen_ids:
                seen_ids.add(url_info['topic_id'])
                unique_urls.append(url_info)

        print(f"✅ 找到 {len(unique_urls)} 个V2EX URL")

        return unique_urls

    def _extract_metadata(self, text: str, url: str) -> tuple[Optional[str], Optional[int]]:
        """从响应文本中提取URL的元数据"""
        # 尝试找到URL所在行
        for line in text.split('\n'):
            if url in line:
                # 提取标题
                title_match = re.search(r'标题[：:](.*?)(?:，|,|回复数|$)', line)
                title = title_match.group(1).strip() if title_match else None

                # 提取回复数
                count_match = re.search(r'(?:回复数|回复)[：:](\d+)', line)
                reply_count = int(count_match.group(1)) if count_match else None

                return title, reply_count

        return None, None

    def save_results(self, urls: List[Dict], output_file: str = "data/perplexity_v2ex_urls.json"):
        """保存搜索结果"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        result = {
            "search_date": datetime.now().isoformat(),
            "total_count": len(urls),
            "platform": "v2ex",
            "urls": urls
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n💾 结果已保存到: {output_path}")

    def display_results(self, urls: List[Dict]):
        """显示搜索结果"""
        print("\n" + "="*60)
        print("🎯 V2EX 搜索结果汇总")
        print("="*60)

        for i, url_info in enumerate(urls, 1):
            title = url_info.get('title', '待采集验证')
            count = url_info.get('estimated_replies', '?')
            print(f"\n{i}. {url_info['url']}")
            print(f"   标题: {title}")
            print(f"   预估回复数: {count}")

        print("\n" + "="*60)
        print(f"📊 总计: {len(urls)} 个V2EX URL")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="使用Perplexity API搜索V2EX高质量讨论URL"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Perplexity API Key"
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
        default="data/perplexity_v2ex_urls.json",
        help="输出文件路径"
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

    print("🚀 Perplexity V2EX URL 搜索工具")
    print("="*60)
    print(f"目标数量: {args.count}")
    print(f"输出文件: {args.output}")
    print("="*60)

    try:
        # 创建搜索器
        searcher = PerplexityV2EXSearcher(api_key)

        # 执行搜索
        urls = searcher.search_v2ex_urls(target_count=args.count)

        # 显示结果
        searcher.display_results(urls)

        # 保存结果
        searcher.save_results(urls, args.output)

        print("\n✅ 搜索完成！")
        print(f"\n💡 下一步:")
        print(f"  1. 查看搜索结果: cat {args.output}")
        print(f"  2. 使用标准爬虫采集V2EX数据（V2EX没有反爬虫）")
        print(f"  3. 如果数量不够，可以再次运行此脚本")

    except Exception as e:
        print(f"\n❌ 搜索失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
