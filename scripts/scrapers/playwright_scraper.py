#!/usr/bin/env python3
"""
使用Playwright浏览器自动化采集知乎数据

用法：
    pixi run python playwright_scraper.py
"""

import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser
import re


class PlaywrightZhihuScraper:
    """使用Playwright采集知乎数据"""

    def __init__(self, config_path: str = "config/target_urls.json"):
        self.config_path = Path(config_path)
        self.output_dir = Path("data/raw")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def scrape_zhihu_question(self, page: Page, url: str) -> Optional[Dict]:
        """采集单个知乎问题"""
        try:
            print(f"\n🔍 正在采集: {url}")

            # 访问页面
            await page.goto(url, wait_until="networkidle", timeout=60000)

            # 等待页面加载
            await page.wait_for_timeout(3000)

            # 提取问题ID
            question_id = url.split("/")[-1]

            # 提取问题标题
            try:
                title_element = await page.query_selector("h1.QuestionHeader-title")
                title = await title_element.inner_text() if title_element else "未知标题"
            except Exception as e:
                print(f"⚠️ 提取标题失败: {e}")
                title = "未知标题"

            # 提取问题描述
            try:
                detail_element = await page.query_selector(".QuestionRichText")
                detail = await detail_element.inner_text() if detail_element else ""
            except:
                detail = ""

            # 提取回答数
            try:
                # 尝试多种选择器
                answer_count_text = None
                selectors = [
                    ".List-headerText span",
                    "h4.List-header-title",
                    ".QuestionAnswers-answerCount"
                ]

                for selector in selectors:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.inner_text()
                        # 提取数字
                        match = re.search(r'(\d+)', text)
                        if match:
                            answer_count_text = match.group(1)
                            break

                answer_count = int(answer_count_text) if answer_count_text else 0
            except Exception as e:
                print(f"⚠️ 提取回答数失败: {e}")
                answer_count = 0

            print(f"   标题: {title}")
            print(f"   回答数: {answer_count}")

            # 检查回答数是否符合要求
            if answer_count < 100:
                print(f"❌ 回答数不足100: {answer_count}")
                return None

            # 滚动页面加载更多回答
            print(f"📜 正在加载回答内容...")
            await self._scroll_to_load_answers(page, max_scrolls=10)

            # 提取回答列表
            answers = []
            try:
                answer_elements = await page.query_selector_all(".List-item")

                for i, answer_elem in enumerate(answer_elements[:100]):  # 最多采集100条回答
                    try:
                        # 提取回答者
                        author_elem = await answer_elem.query_selector(".AuthorInfo-name")
                        author = await author_elem.inner_text() if author_elem else "匿名用户"

                        # 提取回答内容
                        content_elem = await answer_elem.query_selector(".RichContent-inner")
                        content = await content_elem.inner_text() if content_elem else ""

                        # 提取点赞数
                        vote_elem = await answer_elem.query_selector(".VoteButton--up")
                        vote_text = await vote_elem.inner_text() if vote_elem else "0"
                        vote_count = self._extract_number(vote_text)

                        # 提取时间
                        time_elem = await answer_elem.query_selector(".ContentItem-time")
                        created_time = await time_elem.get_attribute("datetime") if time_elem else ""

                        if content:  # 只添加有内容的回答
                            answers.append({
                                "author": author.strip(),
                                "content": content.strip()[:1000],  # 限制长度
                                "vote_count": vote_count,
                                "created_at": created_time
                            })
                    except Exception as e:
                        continue

            except Exception as e:
                print(f"⚠️ 提取回答列表失败: {e}")

            print(f"✅ 成功提取 {len(answers)} 条回答")

            # 构造数据对象
            post_data = {
                "platform": "zhihu",
                "post_type": "question",
                "post_id": question_id,
                "url": url,
                "title": title.strip(),
                "content": detail.strip(),
                "author": "",  # 知乎问题没有单一作者
                "created_at": datetime.now().isoformat(),
                "scraped_at": datetime.now().isoformat(),
                "view_count": 0,
                "like_count": 0,
                "comment_count": answer_count,
                "share_count": 0,
                "comments": answers,
                "is_relevant": True,
                "relevance_note": "Playwright采集"
            }

            return post_data

        except Exception as e:
            print(f"❌ 采集失败 {url}: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def _scroll_to_load_answers(self, page: Page, max_scrolls: int = 10):
        """滚动页面加载更多回答"""
        for i in range(max_scrolls):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1500)

    def _extract_number(self, text: str) -> int:
        """从文本中提取数字"""
        # 处理 "1.2 万" 这种格式
        if "万" in text:
            match = re.search(r'([\d.]+)\s*万', text)
            if match:
                return int(float(match.group(1)) * 10000)

        # 处理普通数字
        match = re.search(r'\d+', text.replace(',', ''))
        return int(match.group()) if match else 0

    async def scrape_all(self):
        """采集所有URL"""
        # 读取配置
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        zhihu_posts = config.get('zhihu_posts', [])

        if not zhihu_posts:
            print("❌ 没有找到知乎URL配置")
            return

        print(f"📚 找到 {len(zhihu_posts)} 个知乎URL")

        # 启动浏览器
        async with async_playwright() as p:
            print("\n🚀 启动浏览器...")
            browser = await p.chromium.launch(
                headless=False,  # 非无头模式，可以看到浏览器操作
                args=['--disable-blink-features=AutomationControlled']
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = await context.new_page()

            # 采集所有URL
            all_posts = []
            success_count = 0
            fail_count = 0

            for i, post_info in enumerate(zhihu_posts, 1):
                url = post_info.get('url')
                if not url:
                    continue

                print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"进度: {i}/{len(zhihu_posts)}")

                post_data = await self.scrape_zhihu_question(page, url)

                if post_data:
                    all_posts.append(post_data)
                    success_count += 1
                    print(f"✅ 成功 ({success_count}/{i})")
                else:
                    fail_count += 1
                    print(f"❌ 失败 ({fail_count}/{i})")

                # 休息一下，避免请求过快
                await page.wait_for_timeout(2000)

            await browser.close()

        # 保存数据
        if all_posts:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"posts_playwright_{timestamp}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_posts, f, ensure_ascii=False, indent=2)

            print(f"\n{'='*60}")
            print(f"✅ 采集完成！")
            print(f"{'='*60}")
            print(f"成功: {success_count} 个")
            print(f"失败: {fail_count} 个")
            print(f"总计: {len(all_posts)} 条数据")
            print(f"保存到: {output_file}")
            print(f"{'='*60}")
        else:
            print("\n❌ 没有采集到任何数据")


async def main():
    scraper = PlaywrightZhihuScraper()
    await scraper.scrape_all()


if __name__ == "__main__":
    asyncio.run(main())
