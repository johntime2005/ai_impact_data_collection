"""
V2EX爬虫模块

V2EX是一个程序员社区，反爬机制相对较弱，但仍需注意频率控制
"""
import re
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from loguru import logger
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scrapers.base_scraper import BaseScraper
from config.config import MIN_COMMENTS_PER_POST


class V2EXScraper(BaseScraper):
    """V2EX爬虫"""

    def __init__(self):
        super().__init__("V2EX")

    def scrape_post(self, url: str) -> Optional[Dict]:
        """
        抓取V2EX主题帖

        Args:
            url: 主题URL (格式: https://www.v2ex.com/t/xxxxx)

        Returns:
            包含主题和回复的数据
        """
        try:
            logger.info(f"开始抓取V2EX主题: {url}")

            # 请求主题页面
            response = self._request_with_retry(url)
            if not response:
                return None

            soup = BeautifulSoup(response.text, 'lxml')

            # 提取主题信息
            post_data = {
                'platform': 'v2ex',
                'type': 'topic',
                'url': url,
                'scraped_at': datetime.now().isoformat(),
            }

            # 提取标题
            title_elem = soup.select_one('h1')
            if title_elem:
                post_data['title'] = title_elem.get_text(strip=True)
            else:
                logger.warning(f"未找到主题标题: {url}")
                post_data['title'] = "未知标题"

            # 提取主题内容
            content_elem = soup.select_one('div.topic_content')
            if content_elem:
                post_data['content'] = content_elem.get_text(strip=True)
            else:
                post_data['content'] = ""

            # 提取作者信息
            author_elem = soup.select_one('a.dark')
            if author_elem:
                post_data['author'] = author_elem.get_text(strip=True)
                post_data['author_url'] = 'https://www.v2ex.com' + author_elem.get('href', '')

            # 提取发布时间
            time_elem = soup.select_one('span.ago')
            if time_elem:
                post_data['created_at'] = time_elem.get_text(strip=True)

            # 提取元数据
            post_data['view_count'] = self._extract_view_count(soup)
            post_data['comment_count'] = self._extract_comment_count(soup)

            # 提取回复
            replies = self._extract_replies(soup)
            post_data['comments'] = replies

            # 更新实际评论数
            post_data['comment_count'] = len(replies)

            logger.info(
                f"成功抓取V2EX主题: {post_data['title']} - "
                f"{post_data['comment_count']}个回复"
            )
            return post_data

        except Exception as e:
            logger.error(f"抓取V2EX内容失败: {url} - {str(e)}")
            return None

    def _extract_view_count(self, soup: BeautifulSoup) -> int:
        """
        提取浏览次数

        Args:
            soup: BeautifulSoup对象

        Returns:
            浏览次数
        """
        try:
            # V2EX的浏览数在 "xxx 次点击" 文本中
            count_elem = soup.select_one('span.topic_info')
            if count_elem:
                text = count_elem.get_text()
                match = re.search(r'(\d+)\s*次点击', text)
                if match:
                    return int(match.group(1))
        except Exception as e:
            logger.debug(f"提取浏览数失败: {e}")

        return 0

    def _extract_comment_count(self, soup: BeautifulSoup) -> int:
        """
        提取评论数

        Args:
            soup: BeautifulSoup对象

        Returns:
            评论数
        """
        try:
            # V2EX的回复数在 "xxx 条回复" 文本中
            count_elem = soup.select_one('span.topic_info')
            if count_elem:
                text = count_elem.get_text()
                match = re.search(r'(\d+)\s*条回复', text)
                if match:
                    return int(match.group(1))
        except Exception as e:
            logger.debug(f"提取评论数失败: {e}")

        return 0

    def _extract_replies(self, soup: BeautifulSoup) -> List[Dict]:
        """
        提取回复列表

        Args:
            soup: BeautifulSoup对象

        Returns:
            回复列表
        """
        replies = []

        # 查找所有回复项
        reply_items = soup.select('div.cell[id^="r_"]')

        for item in reply_items:
            try:
                reply = {}

                # 回复作者
                author_elem = item.select_one('strong a')
                if author_elem:
                    reply['author'] = author_elem.get_text(strip=True)
                    reply['author_url'] = 'https://www.v2ex.com' + author_elem.get('href', '')
                else:
                    continue  # 没有作者的跳过

                # 回复内容
                content_elem = item.select_one('div.reply_content')
                if content_elem:
                    reply['content'] = content_elem.get_text(strip=True)
                else:
                    continue  # 没有内容的跳过

                # 回复时间
                time_elem = item.select_one('span.ago')
                if time_elem:
                    reply['created_at'] = time_elem.get_text(strip=True)

                # 点赞数（V2EX叫"感谢"）
                thank_elem = item.select_one('span.small.fade')
                if thank_elem:
                    thank_text = thank_elem.get_text()
                    match = re.search(r'(\d+)', thank_text)
                    if match:
                        reply['upvotes'] = int(match.group(1))
                    else:
                        reply['upvotes'] = 0
                else:
                    reply['upvotes'] = 0

                # 楼层号
                no_elem = item.select_one('span.no')
                if no_elem:
                    reply['floor'] = no_elem.get_text(strip=True)

                # 回复URL（通过ID构建）
                reply_id = item.get('id', '')
                if reply_id:
                    reply['url'] = f"{soup.find('base', href=True)['href'] if soup.find('base', href=True) else 'https://www.v2ex.com/'}#{reply_id}"

                replies.append(reply)

            except Exception as e:
                logger.debug(f"解析单个回复失败: {e}")
                continue

        return replies

    def validate_post(self, post_data: Dict) -> bool:
        """
        验证帖子数据是否符合要求

        Args:
            post_data: 帖子数据

        Returns:
            是否符合要求
        """
        if not post_data:
            return False

        # 检查评论数量
        comment_count = post_data.get('comment_count', 0)
        if comment_count < MIN_COMMENTS_PER_POST:
            logger.warning(
                f"回复数不足: {post_data.get('title', 'Unknown')} - "
                f"{comment_count}/{MIN_COMMENTS_PER_POST}"
            )
            return False

        # 检查必要字段
        required_fields = ['title', 'url', 'platform']
        for field in required_fields:
            if field not in post_data:
                logger.warning(f"缺少必要字段: {field}")
                return False

        return True

    def search_topics(
        self,
        keyword: str,
        max_pages: int = 5
    ) -> List[str]:
        """
        搜索相关主题并返回URL列表

        注意：V2EX搜索功能可能需要登录或使用API

        Args:
            keyword: 搜索关键词
            max_pages: 最大搜索页数

        Returns:
            主题URL列表
        """
        logger.info(f"搜索V2EX主题: {keyword}")

        # V2EX搜索相对复杂，这里提供基本框架
        # 实际使用时建议手动搜索后将URL添加到config中

        topic_urls = []

        logger.warning("V2EX搜索功能需要手动完成，建议直接在配置文件中添加目标URL")

        return topic_urls
