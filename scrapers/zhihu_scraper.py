"""
知乎爬虫模块

注意事项:
1. 知乎需要登录才能看到完整评论，建议手动获取Cookie后配置
2. 知乎有较强的反爬机制，请合理控制请求频率
3. 此实现为基础版本，可能需要根据实际情况调整
"""
import re
import json
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


class ZhihuScraper(BaseScraper):
    """知乎爬虫"""

    def __init__(self, cookie: Optional[str] = None):
        """
        初始化知乎爬虫

        Args:
            cookie: 知乎登录Cookie（可选，但建议提供以获取完整数据）
        """
        super().__init__("知乎")
        self.cookie = cookie
        if cookie:
            self.session.headers.update({'Cookie': cookie})
            logger.info("已配置知乎Cookie")

    def scrape_post(self, url: str) -> Optional[Dict]:
        """
        抓取知乎问题/文章

        Args:
            url: 知乎问题或文章URL

        Returns:
            包含问题/文章和回答/评论的数据
        """
        try:
            # 判断URL类型
            if '/question/' in url:
                return self._scrape_question(url)
            elif '/p/' in url:
                return self._scrape_article(url)
            else:
                logger.error(f"不支持的URL类型: {url}")
                return None

        except Exception as e:
            logger.error(f"抓取知乎内容失败: {url} - {str(e)}")
            return None

    def _scrape_question(self, url: str) -> Optional[Dict]:
        """
        抓取知乎问题

        Args:
            url: 问题URL (格式: https://www.zhihu.com/question/xxxxx)

        Returns:
            问题数据
        """
        logger.info(f"开始抓取知乎问题: {url}")

        # 请求问题页面
        response = self._request_with_retry(url)
        if not response:
            return None

        soup = BeautifulSoup(response.text, 'lxml')

        # 提取问题信息
        post_data = {
            'platform': 'zhihu',
            'type': 'question',
            'url': url,
            'scraped_at': datetime.now().isoformat(),
        }

        # 提取问题标题
        title_elem = soup.select_one('h1.QuestionHeader-title')
        if title_elem:
            post_data['title'] = title_elem.get_text(strip=True)
        else:
            logger.warning(f"未找到问题标题: {url}")
            post_data['title'] = "未知标题"

        # 提取问题详情
        detail_elem = soup.select_one('div.QuestionRichText span[itemprop="text"]')
        if detail_elem:
            post_data['detail'] = detail_elem.get_text(strip=True)
        else:
            post_data['detail'] = ""

        # 提取问题元信息
        post_data['view_count'] = self._extract_number(soup, 'strong.NumberBoard-itemValue', '浏览')
        post_data['follow_count'] = self._extract_number(soup, 'button.Button.FollowButton', '关注')

        # 尝试从页面脚本中提取问题创建时间
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'createdTime' in script.string:
                try:
                    # 简单的正则匹配，实际可能需要更复杂的解析
                    match = re.search(r'"createdTime":(\d+)', script.string)
                    if match:
                        timestamp = int(match.group(1))
                        post_data['created_at'] = datetime.fromtimestamp(timestamp).isoformat()
                        break
                except Exception as e:
                    logger.debug(f"解析创建时间失败: {e}")

        # 提取回答（作为"评论"）
        answers = self._extract_answers(soup, url)
        post_data['comments'] = answers
        post_data['comment_count'] = len(answers)

        logger.info(f"成功抓取知乎问题: {post_data['title']} - {post_data['comment_count']}个回答")
        return post_data

    def _scrape_article(self, url: str) -> Optional[Dict]:
        """
        抓取知乎文章

        Args:
            url: 文章URL (格式: https://zhuanlan.zhihu.com/p/xxxxx)

        Returns:
            文章数据
        """
        logger.info(f"开始抓取知乎文章: {url}")

        response = self._request_with_retry(url)
        if not response:
            return None

        soup = BeautifulSoup(response.text, 'lxml')

        post_data = {
            'platform': 'zhihu',
            'type': 'article',
            'url': url,
            'scraped_at': datetime.now().isoformat(),
        }

        # 提取文章标题
        title_elem = soup.select_one('h1.Post-Title')
        if title_elem:
            post_data['title'] = title_elem.get_text(strip=True)
        else:
            post_data['title'] = "未知标题"

        # 提取文章内容
        content_elem = soup.select_one('div.Post-RichTextContainer')
        if content_elem:
            post_data['content'] = content_elem.get_text(strip=True)[:500]  # 只保留前500字符
        else:
            post_data['content'] = ""

        # 提取作者信息
        author_elem = soup.select_one('div.AuthorInfo-name a')
        if author_elem:
            post_data['author'] = author_elem.get_text(strip=True)

        # 提取发布时间
        time_elem = soup.select_one('div.ContentItem-time')
        if time_elem:
            post_data['created_at'] = time_elem.get_text(strip=True)

        # 文章的评论需要通过API获取，这里简化处理
        post_data['comments'] = []
        post_data['comment_count'] = 0
        logger.warning(f"知乎文章评论需要单独API抓取，当前未实现: {url}")

        return post_data

    def _extract_answers(self, soup: BeautifulSoup, question_url: str) -> List[Dict]:
        """
        提取问题的回答列表

        Args:
            soup: 页面BeautifulSoup对象
            question_url: 问题URL

        Returns:
            回答列表
        """
        answers = []

        # 查找回答卡片
        answer_items = soup.select('div.List-item')

        for item in answer_items:
            try:
                answer = {}

                # 回答作者
                author_elem = item.select_one('a.AuthorInfo-name')
                if author_elem:
                    answer['author'] = author_elem.get_text(strip=True)
                else:
                    answer['author'] = "匿名用户"

                # 回答内容
                content_elem = item.select_one('div.RichContent-inner span[itemprop="text"]')
                if content_elem:
                    answer['content'] = content_elem.get_text(strip=True)
                else:
                    continue  # 没有内容的跳过

                # 点赞数
                vote_elem = item.select_one('button.VoteButton--up')
                if vote_elem:
                    vote_text = vote_elem.get_text(strip=True)
                    answer['upvotes'] = self._parse_count_text(vote_text)
                else:
                    answer['upvotes'] = 0

                # 回答时间
                time_elem = item.select_one('span.ContentItem-time')
                if time_elem:
                    answer['created_at'] = time_elem.get_text(strip=True)

                # 回答URL
                answer_link = item.select_one('a.ContentItem-title')
                if answer_link and answer_link.get('href'):
                    answer['url'] = 'https:' + answer_link['href'] if answer_link['href'].startswith('//') else answer_link['href']

                answers.append(answer)

            except Exception as e:
                logger.debug(f"解析单个回答失败: {e}")
                continue

        return answers

    def _extract_number(self, soup: BeautifulSoup, selector: str, keyword: str = None) -> int:
        """
        从页面提取数字

        Args:
            soup: BeautifulSoup对象
            selector: CSS选择器
            keyword: 关键词过滤

        Returns:
            提取的数字
        """
        try:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                return self._parse_count_text(text)
        except Exception:
            pass
        return 0

    @staticmethod
    def _parse_count_text(text: str) -> int:
        """
        解析计数文本（如 "1.2万"、"1234" 等）

        Args:
            text: 计数文本

        Returns:
            数字
        """
        text = text.strip()
        if not text or text == '赞同':
            return 0

        try:
            # 处理 "万" 单位
            if '万' in text:
                num = float(re.search(r'[\d.]+', text).group())
                return int(num * 10000)
            # 处理纯数字
            elif text.isdigit():
                return int(text)
            # 处理带逗号的数字
            else:
                num_str = re.sub(r'[^\d]', '', text)
                return int(num_str) if num_str else 0
        except Exception:
            return 0

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
                f"评论数不足: {post_data.get('title', 'Unknown')} - "
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
