#!/usr/bin/env python3
"""
主程序入口 - 数据采集和分析

使用方法:
    python main.py scrape     # 执行数据采集
    python main.py analyze    # 执行数据分析
    python main.py full       # 执行完整流程
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR, PROJECT_ROOT
from utils.logger import setup_logger
from utils.file_handler import save_json, load_json, save_posts_batch
from scrapers.zhihu_scraper import ZhihuScraper
from scrapers.v2ex_scraper import V2EXScraper
from analytics.data_cleaner import DataCleaner
from analytics.quality_analyzer import QualityAnalyzer
from analytics.text_analyzer import TextAnalyzer
from analytics.report_generator import ReportGenerator


class DataCollectionApp:
    """数据采集应用主类"""

    def __init__(self):
        # 初始化日志
        log_dir = PROJECT_ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        setup_logger(
            log_file=log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log",
            level="INFO"
        )

        logger.info("=" * 60)
        logger.info("数据采集系统启动")
        logger.info("=" * 60)

        self.scrapers = {
            'zhihu': ZhihuScraper(),
            'v2ex': V2EXScraper()
        }

    def scrape_data(self) -> Path:
            """
            执行数据采集

            Returns:
                保存的数据文件路径
            """
            logger.info("【步骤1】开始数据采集")

            # 加载目标URL配置
            config_path = PROJECT_ROOT / "config" / "target_urls.json"
            if not config_path.exists():
                logger.error(f"配置文件不存在: {config_path}")
                logger.error("请先在config/target_urls.json中配置要采集的URL")
                sys.exit(1)

            targets = load_json(config_path)

            # 验证配置格式，确保是字典并包含期望的列表
            if not isinstance(targets, dict):
                logger.error(f"配置文件格式错误，期望包含对象映射：{config_path}")
                sys.exit(1)

            zhihu_posts = targets['zhihu_posts'] if ('zhihu_posts' in targets and isinstance(targets['zhihu_posts'], list)) else []
            v2ex_posts = targets['v2ex_posts'] if ('v2ex_posts' in targets and isinstance(targets['v2ex_posts'], list)) else []

            logger.info(f"加载配置完成: {len(zhihu_posts)} 个知乎帖子, {len(v2ex_posts)} 个V2EX帖子")

            all_posts = []

            # 采集知乎数据
            if zhihu_posts:
                logger.info("开始采集知乎数据...")
                zhihu_scraper = self.scrapers.get('zhihu')
                if zhihu_scraper is None:
                    logger.error("未找到知乎采集器实例，跳过知乎数据采集")
                else:
                    for post_info in zhihu_posts:
                        if not isinstance(post_info, dict):
                            logger.warning("跳过格式不正确的知乎条目（期望对象）")
                            continue

                        if not post_info.get('manual_checked', False):
                            logger.warning(f"跳过未人工确认的URL: {post_info.get('url')}")
                            continue

                        url = post_info.get('url')
                        if not url:
                            logger.warning("跳过缺少URL的知乎条目")
                            continue

                        logger.info(f"采集: {url}")

                        try:
                            post_data = zhihu_scraper.scrape_post(url)
                            if post_data and zhihu_scraper.validate_post(post_data):
                                # 添加人工标注的信息
                                post_data['is_relevant'] = True
                                post_data['relevance_note'] = post_info.get('relevance_note', '')
                                all_posts.append(post_data)
                                logger.success(f"✓ 采集成功: {post_data.get('title')}")
                            else:
                                logger.warning(f"✗ 数据验证失败: {url}")
                        except Exception as e:
                            logger.error(f"✗ 采集失败: {url} - {e}")

            # 采集V2EX数据
            if v2ex_posts:
                logger.info("开始采集V2EX数据...")
                v2ex_scraper = self.scrapers.get('v2ex')
                if v2ex_scraper is None:
                    logger.error("未找到V2EX采集器实例，跳过V2EX数据采集")
                else:
                    for post_info in v2ex_posts:
                        if not isinstance(post_info, dict):
                            logger.warning("跳过格式不正确的V2EX条目（期望对象）")
                            continue

                        if not post_info.get('manual_checked', False):
                            logger.warning(f"跳过未人工确认的URL: {post_info.get('url')}")
                            continue

                        url = post_info.get('url')
                        if not url:
                            logger.warning("跳过缺少URL的V2EX条目")
                            continue

                        logger.info(f"采集: {url}")

                        try:
                            post_data = v2ex_scraper.scrape_post(url)
                            if post_data and v2ex_scraper.validate_post(post_data):
                                post_data['is_relevant'] = True
                                post_data['relevance_note'] = post_info.get('relevance_note', '')
                                all_posts.append(post_data)
                                logger.success(f"✓ 采集成功: {post_data.get('title')}")
                            else:
                                logger.warning(f"✗ 数据验证失败: {url}")
                        except Exception as e:
                            logger.error(f"✗ 采集失败: {url} - {e}")

            # 保存原始数据
            if all_posts:
                try:
                    output_file = save_posts_batch(all_posts, RAW_DATA_DIR, format='json')
                    logger.success(f"【步骤1完成】数据采集完成，共 {len(all_posts)} 条帖子")
                    logger.success(f"原始数据已保存: {output_file}")
                    return output_file
                except Exception as e:
                    logger.exception(f"保存采集数据失败: {e}")
                    sys.exit(1)
            else:
                logger.error("【步骤1失败】没有采集到任何有效数据")
                sys.exit(1)

    def analyze_data(self, data_file=None) -> Dict:
            """
            执行数据分析

            Args:
                data_file: 数据文件路径，None则使用最新的

            Returns:
                分析结果
            """
            logger.info("【步骤2】开始数据分析")

            # 确定要加载的数据文件
            if data_file is None:
                raw_files = list(RAW_DATA_DIR.glob("posts_*.json"))
                if not raw_files:
                    logger.error("未找到数据文件，请先执行采集")
                    sys.exit(1)
                data_file = max(raw_files, key=lambda p: p.stat().st_mtime)
            else:
                # 接受 Path、str 等，尝试转换为 Path
                if not isinstance(data_file, Path):
                    try:
                        data_file = Path(data_file)
                    except Exception:
                        logger.error(f"传入的数据文件路径无效: {data_file}")
                        sys.exit(1)

            if not data_file.exists():
                logger.error(f"数据文件不存在: {data_file}")
                sys.exit(1)

            logger.info(f"加载数据: {data_file}")

            try:
                posts_raw = load_json(data_file)
            except Exception as e:
                logger.exception(f"加载数据失败: {e}")
                sys.exit(1)

            # 规范化数据格式，确保传入清洗器的是 List[Dict]
            posts_list = None
            if isinstance(posts_raw, list):
                posts_list = posts_raw
            elif isinstance(posts_raw, dict):
                # 常见包装字段
                for key in ("posts", "data", "items", "results"):
                    if key in posts_raw and isinstance(posts_raw[key], list):
                        posts_list = posts_raw[key]
                        break

                # 如果没有找到常见字段，尝试将 dict 的 values 中的 dict 项目收集为列表
                if posts_list is None:
                    candidate_values = [v for v in posts_raw.values() if isinstance(v, dict)]
                    if candidate_values:
                        posts_list = candidate_values

            if posts_list is None:
                logger.error("加载的数据格式不符合预期，无法提取帖子列表（期望 List[Dict]）")
                sys.exit(1)

            logger.info(f"加载完成，共 {len(posts_list)} 条帖子")

            # 数据清洗
            logger.info("执行数据清洗...")
            cleaner = DataCleaner()
            try:
                cleaned_posts = cleaner.clean_posts(posts_list)
            except Exception as e:
                logger.exception(f"数据清洗失败: {e}")
                sys.exit(1)

            # 确保目录存在并保存清洗后的数据
            try:
                PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
                cleaned_file = PROCESSED_DATA_DIR / f"cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                save_json(cleaned_posts, cleaned_file, pretty=True)
                logger.success(f"清洗后数据已保存: {cleaned_file}")
            except Exception as e:
                logger.exception(f"保存清洗后数据失败: {e}")
                sys.exit(1)

            # 质量分析
            logger.info("执行质量分析...")
            quality_analyzer = QualityAnalyzer()
            try:
                quality_result = quality_analyzer.analyze(cleaned_posts)
                summary = quality_analyzer.generate_summary()
                if summary:
                    logger.info("\n" + summary)
            except Exception as e:
                logger.exception(f"质量分析失败: {e}")
                sys.exit(1)

            # 文本分析
            logger.info("执行文本分析...")
            text_analyzer = TextAnalyzer()
            try:
                text_result = text_analyzer.analyze_texts(cleaned_posts)
            except Exception as e:
                logger.exception(f"文本分析失败: {e}")
                sys.exit(1)

            # 生成报告
            logger.info("生成分析报告...")
            try:
                REPORTS_DIR.mkdir(parents=True, exist_ok=True)
                report_generator = ReportGenerator()
                report_file = REPORTS_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                report_generator.generate_report(
                    cleaned_posts,
                    quality_result,
                    text_result,
                    report_file
                )
                logger.success(f"【步骤2完成】分析报告已生成: {report_file}")
            except Exception as e:
                logger.exception(f"生成报告失败: {e}")
                sys.exit(1)

            return {
                'cleaned_posts': cleaned_posts,
                'quality_result': quality_result,
                'text_result': text_result,
                'report_file': report_file
            }

    def run_full_pipeline(self):
        """执行完整流程"""
        logger.info("=" * 60)
        logger.info("开始执行完整数据采集和分析流程")
        logger.info("=" * 60)

        # 1. 数据采集
        data_file = self.scrape_data()

        # 2. 数据分析
        result = self.analyze_data(data_file)

        logger.info("=" * 60)
        logger.success("✓ 完整流程执行完毕")
        logger.info(f"✓ 分析报告: {result['report_file']}")
        logger.info("=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="大模型对IT行业影响 - 数据采集与分析系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py scrape              # 仅执行数据采集
  python main.py analyze             # 仅执行数据分析（使用最新数据）
  python main.py analyze -f data.json # 分析指定数据文件
  python main.py full                # 执行完整流程
        """
    )

    parser.add_argument(
        'command',
        choices=['scrape', 'analyze', 'full'],
        help='执行的命令'
    )

    parser.add_argument(
        '-f', '--file',
        type=Path,
        help='指定要分析的数据文件路径'
    )

    args = parser.parse_args()

    # 创建应用实例
    app = DataCollectionApp()

    try:
        if args.command == 'scrape':
            app.scrape_data()
        elif args.command == 'analyze':
            app.analyze_data(args.file)
        elif args.command == 'full':
            app.run_full_pipeline()
    except KeyboardInterrupt:
        logger.warning("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"程序执行出错: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
