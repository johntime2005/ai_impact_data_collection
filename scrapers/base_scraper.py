"""
基础爬虫类 - 提供通用的爬虫功能
"""
import time
import random
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from loguru import logger
import sys

# 添加项目路径
sys.path.append('..')
from config.config import (
    USER_AGENTS, REQUEST_TIMEOUT, REQUEST_DELAY_MIN,
    REQUEST_DELAY_MAX, MAX_RETRIES
)


class BaseScraper(ABC):
    """爬虫基类"""

    def __init__(self, name: str):
        self.name = name
        self.session = requests.Session()
        logger.info(f"初始化 {name} 爬虫")

    def _get_headers(self) -> Dict[str, str]:
        """获取随机请求头"""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def _request_with_retry(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        带重试机制的请求

        Args:
            url: 请求URL
            method: 请求方法
            **kwargs: 其他请求参数

        Returns:
            响应对象，失败返回None
        """
        for attempt in range(MAX_RETRIES):
            try:
                # 添加随机延迟，避免请求过快
                time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

                # 发送请求
                headers = kwargs.pop('headers', {})
                headers.update(self._get_headers())

                if method.upper() == 'GET':
                    response = self.session.get(
                        url,
                        headers=headers,
                        timeout=REQUEST_TIMEOUT,
                        **kwargs
                    )
                else:
                    response = self.session.post(
                        url,
                        headers=headers,
                        timeout=REQUEST_TIMEOUT,
                        **kwargs
                    )

                response.raise_for_status()
                logger.debug(f"成功请求: {url}")
                return response

            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {url} - {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"达到最大重试次数，放弃请求: {url}")
                    return None
                # 重试前等待更长时间
                time.sleep(random.uniform(3, 6))

        return None

    @abstractmethod
    def scrape_post(self, url: str) -> Optional[Dict]:
        """
        抓取单个帖子的内容和评论

        Args:
            url: 帖子URL

        Returns:
            包含帖子信息和评论的字典
        """
        pass

    @abstractmethod
    def validate_post(self, post_data: Dict) -> bool:
        """
        验证帖子数据是否符合要求

        Args:
            post_data: 帖子数据

        Returns:
            是否符合要求
        """
        pass

    def close(self):
        """关闭会话"""
        self.session.close()
        logger.info(f"关闭 {self.name} 爬虫")
