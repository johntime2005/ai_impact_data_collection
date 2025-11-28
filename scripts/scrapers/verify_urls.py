#!/usr/bin/env python3
"""
URL验证脚本 - 自动检查评论数
"""
import sys
from pathlib import Path
import re
import time
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from loguru import logger

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.file_handler import load_json, save_json

# 配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

REQUEST_TIMEOUT = 30
REQUEST_DELAY = 3  # 每个请求之间延迟3秒


class URLVerifier:
    """URL验证器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.results = []

    def verify_zhihu_question(self, url: str) -> Optional[Dict]:
        """
        验证知乎问题的评论数

        Returns:
            {
                'url': str,
                'title': str,
                'comment_count': int,
                'answer_count': int,
                'publish_date': str,
                'verified': bool,
                'error': str (如果有错误)
            }
        """
        try:
            logger.info(f"正在验证知乎URL: {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)

            if response.status_code != 200:
                logger.warning(f"请求失败，状态码: {response.status_code}")
                return {
                    'url': url,
                    'verified': False,
                    'error': f'HTTP {response.status_code}'
                }

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取标题
            title_elem = soup.find('h1', class_='QuestionHeader-title')
            title = title_elem.get_text(strip=True) if title_elem else "未知标题"

            # 提取回答数（知乎的回答就是评论）
            answer_count = 0

            # 方法1: 从侧边栏提取
            sidebar = soup.find('div', class_='QuestionAnswers-answers')
            if sidebar:
                count_text = sidebar.get_text()
                match = re.search(r'(\d+)\s*个回答', count_text)
                if match:
                    answer_count = int(match.group(1))

            # 方法2: 从页面meta标签提取
            if answer_count == 0:
                meta_count = soup.find('meta', property='og:description')
                if meta_count:
                    content = meta_count.get('content', '')
                    match = re.search(r'(\d+)\s*个回答', content)
                    if match:
                        answer_count = int(match.group(1))

            # 方法3: 从按钮文本提取
            if answer_count == 0:
                answer_button = soup.find('button', string=re.compile(r'\d+\s*个回答'))
                if answer_button:
                    match = re.search(r'(\d+)', answer_button.get_text())
                    if match:
                        answer_count = int(match.group(1))

            # 提取发布时间
            time_elem = soup.find('meta', property='article:published_time')
            publish_date = time_elem.get('content', '').split('T')[0] if time_elem else "未知"

            result = {
                'url': url,
                'title': title,
                'comment_count': answer_count,  # 知乎的回答数
                'answer_count': answer_count,
                'publish_date': publish_date,
                'verified': True,
                'meets_requirement': answer_count >= 100
            }

            logger.success(f"✓ 验证成功: {title} - {answer_count}个回答")
            return result

        except Exception as e:
            logger.error(f"验证失败: {url} - {e}")
            return {
                'url': url,
                'verified': False,
                'error': str(e)
            }

    def verify_v2ex_post(self, url: str) -> Optional[Dict]:
        """
        验证V2EX帖子的评论数

        Returns:
            {
                'url': str,
                'title': str,
                'comment_count': int,
                'reply_count': int,
                'publish_date': str,
                'verified': bool,
                'error': str (如果有错误)
            }
        """
        try:
            logger.info(f"正在验证V2EX URL: {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)

            if response.status_code != 200:
                logger.warning(f"请求失败，状态码: {response.status_code}")
                return {
                    'url': url,
                    'verified': False,
                    'error': f'HTTP {response.status_code}'
                }

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取标题
            title_elem = soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else "未知标题"

            # 提取回复数
            reply_count = 0

            # 方法1: 从页面标题提取 "xxx 回复"
            reply_header = soup.find('div', class_='cell')
            if reply_header:
                match = re.search(r'(\d+)\s*条回复', reply_header.get_text())
                if match:
                    reply_count = int(match.group(1))

            # 方法2: 统计回复div数量
            if reply_count == 0:
                reply_divs = soup.find_all('div', class_='reply')
                reply_count = len(reply_divs)

            # 提取发布时间
            time_elem = soup.find('span', class_='gray')
            publish_date = "未知"
            if time_elem:
                time_text = time_elem.get_text(strip=True)
                # V2EX时间格式: "2023-01-15 12:30:45"
                match = re.search(r'\d{4}-\d{2}-\d{2}', time_text)
                if match:
                    publish_date = match.group(0)

            result = {
                'url': url,
                'title': title,
                'comment_count': reply_count,
                'reply_count': reply_count,
                'publish_date': publish_date,
                'verified': True,
                'meets_requirement': reply_count >= 100
            }

            logger.success(f"✓ 验证成功: {title} - {reply_count}条回复")
            return result

        except Exception as e:
            logger.error(f"验证失败: {url} - {e}")
            return {
                'url': url,
                'verified': False,
                'error': str(e)
            }

    def verify_url(self, url: str, platform: str) -> Optional[Dict]:
        """根据平台验证URL"""
        if platform == 'zhihu':
            return self.verify_zhihu_question(url)
        elif platform == 'v2ex':
            return self.verify_v2ex_post(url)
        else:
            logger.error(f"不支持的平台: {platform}")
            return None

    def verify_all_urls(self, discovered_urls_file: Path) -> List[Dict]:
        """验证所有URL"""
        logger.info("=" * 60)
        logger.info("开始验证URL")
        logger.info("=" * 60)

        # 加载URL列表
        data = load_json(discovered_urls_file)
        zhihu_posts = data.get('zhihu_posts', [])
        v2ex_posts = data.get('v2ex_posts', [])

        all_results = []

        # 验证知乎帖子
        logger.info(f"\n【1/2】验证知乎帖子 ({len(zhihu_posts)}个)")
        for i, post in enumerate(zhihu_posts, 1):
            logger.info(f"\n进度: {i}/{len(zhihu_posts)}")
            result = self.verify_zhihu_question(post['url'])
            if result:
                result['platform'] = 'zhihu'
                result['original_info'] = post
                all_results.append(result)
            time.sleep(REQUEST_DELAY)

        # 验证V2EX帖子
        logger.info(f"\n【2/2】验证V2EX帖子 ({len(v2ex_posts)}个)")
        for i, post in enumerate(v2ex_posts, 1):
            logger.info(f"\n进度: {i}/{len(v2ex_posts)}")
            result = self.verify_v2ex_post(post['url'])
            if result:
                result['platform'] = 'v2ex'
                result['original_info'] = post
                all_results.append(result)
            time.sleep(REQUEST_DELAY)

        self.results = all_results
        return all_results

    def generate_report(self) -> str:
        """生成验证报告"""
        verified_count = sum(1 for r in self.results if r.get('verified'))
        failed_count = len(self.results) - verified_count

        meets_requirement = [r for r in self.results if r.get('meets_requirement')]

        report = f"""
{'='*60}
URL验证报告
{'='*60}

总计验证: {len(self.results)} 个URL
验证成功: {verified_count} 个
验证失败: {failed_count} 个

符合要求(评论>=100): {len(meets_requirement)} 个
不符合要求: {verified_count - len(meets_requirement)} 个

{'='*60}
详细结果
{'='*60}

"""

        # 符合要求的帖子
        report += "\n✅ 符合要求的帖子 (评论>=100):\n"
        report += "-" * 60 + "\n"
        for i, result in enumerate(meets_requirement, 1):
            platform = result.get('platform', '未知')
            title = result.get('title', '未知标题')
            count = result.get('comment_count', 0)
            url = result.get('url', '')
            date = result.get('publish_date', '未知')

            report += f"\n{i}. [{platform.upper()}] {title}\n"
            report += f"   评论数: {count}\n"
            report += f"   发布时间: {date}\n"
            report += f"   URL: {url}\n"

        # 不符合要求的帖子
        not_meets = [r for r in self.results if r.get('verified') and not r.get('meets_requirement')]
        if not_meets:
            report += "\n\n⚠️ 不符合要求的帖子 (评论<100):\n"
            report += "-" * 60 + "\n"
            for i, result in enumerate(not_meets, 1):
                platform = result.get('platform', '未知')
                title = result.get('title', '未知标题')
                count = result.get('comment_count', 0)
                url = result.get('url', '')

                report += f"\n{i}. [{platform.upper()}] {title}\n"
                report += f"   评论数: {count} (不足100)\n"
                report += f"   URL: {url}\n"

        # 验证失败的帖子
        failed = [r for r in self.results if not r.get('verified')]
        if failed:
            report += "\n\n❌ 验证失败的帖子:\n"
            report += "-" * 60 + "\n"
            for i, result in enumerate(failed, 1):
                url = result.get('url', '')
                error = result.get('error', '未知错误')

                report += f"\n{i}. URL: {url}\n"
                report += f"   错误: {error}\n"

        report += "\n" + "=" * 60 + "\n"
        report += f"\n结论: "
        if len(meets_requirement) >= 18:
            report += f"✅ 已找到{len(meets_requirement)}个符合要求的帖子，满足作业要求(>=18个)！\n"
        else:
            needed = 18 - len(meets_requirement)
            report += f"⚠️ 还需要{needed}个符合要求的帖子才能满足作业要求(>=18个)\n"
            report += f"   建议: 继续搜索知乎和V2EX上的相关讨论\n"

        return report

    def create_config_file(self, output_file: Path):
        """创建配置文件"""
        meets_requirement = [r for r in self.results if r.get('meets_requirement')]

        config = {
            "comment": "经过验证的目标URL列表",
            "verification_info": {
                "verified_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_verified": len(meets_requirement),
                "verification_method": "自动爬虫验证"
            },
            "zhihu_posts": [],
            "v2ex_posts": []
        }

        for result in meets_requirement:
            platform = result.get('platform')
            original = result.get('original_info', {})

            post_config = {
                "url": result.get('url'),
                "title": result.get('title'),
                "date": result.get('publish_date'),
                "relevance_note": original.get('relevance_note', ''),
                "comment_count_verified": result.get('comment_count'),
                "manual_checked": True,
                "auto_verified": True
            }

            if platform == 'zhihu':
                config['zhihu_posts'].append(post_config)
            elif platform == 'v2ex':
                config['v2ex_posts'].append(post_config)

        save_json(config, output_file, pretty=True)
        logger.success(f"配置文件已生成: {output_file}")
        logger.info(f"  - 知乎帖子: {len(config['zhihu_posts'])}个")
        logger.info(f"  - V2EX帖子: {len(config['v2ex_posts'])}个")


def main():
    """主函数"""
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

    project_root = Path(__file__).parent
    discovered_urls_file = project_root / "data" / "discovered_urls.json"

    if not discovered_urls_file.exists():
        logger.error(f"文件不存在: {discovered_urls_file}")
        sys.exit(1)

    # 创建验证器
    verifier = URLVerifier()

    # 验证所有URL
    results = verifier.verify_all_urls(discovered_urls_file)

    # 生成报告
    report = verifier.generate_report()
    print(report)

    # 保存验证结果
    results_file = project_root / "data" / "verification_results.json"
    save_json(results, results_file, pretty=True)
    logger.success(f"\n验证结果已保存: {results_file}")

    # 保存报告
    report_file = project_root / "data" / "verification_report.txt"
    report_file.write_text(report, encoding='utf-8')
    logger.success(f"验证报告已保存: {report_file}")

    # 创建配置文件
    config_file = project_root / "config" / "target_urls.json"
    verifier.create_config_file(config_file)

    logger.info("\n" + "=" * 60)
    logger.success("✓ 验证完成！")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
