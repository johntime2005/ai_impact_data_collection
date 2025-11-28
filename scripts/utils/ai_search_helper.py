#!/usr/bin/env python3
"""
AI搜索助手 - 自动发现相关讨论URL

使用方法:
    python ai_search_helper.py discover     # 开始AI辅助搜索
    python ai_search_helper.py evaluate     # 评估已采集的数据相关性
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger

from ai_search.relevance_evaluator import RelevanceEvaluator
from ai_search.url_discoverer import URLDiscoverer
from config.config import PROJECT_ROOT
from utils.file_handler import load_json, save_json
from utils.logger import setup_logger


class AISearchHelper:
    """AI搜索助手应用"""

    def __init__(self, use_perplexity: bool = False, api_key: str = None):
        # 初始化日志
        log_dir = PROJECT_ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        setup_logger(
            log_file=log_dir / f"ai_search_{datetime.now().strftime('%Y%m%d')}.log",
            level="INFO",
        )

        self.discoverer = URLDiscoverer(use_perplexity, api_key)
        self.evaluator = RelevanceEvaluator()

        logger.info("AI搜索助手初始化完成")

    def run_discovery(self):
        """运行URL发现流程"""
        logger.info("=" * 60)
        logger.info("🤖 AI辅助URL发现")
        logger.info("=" * 60)

        # 获取搜索指令
        instructions = self.discoverer.discover_urls_interactive()

        logger.info("\n" + "=" * 60)
        logger.info("📋 搜索任务清单")
        logger.info("=" * 60)

        print("\n请AI助手（Claude/GPT等）执行以下搜索查询：\n")

        for i, query in enumerate(instructions["search_queries"], 1):
            print(f"{i}. {query}")

        print(f"\n目标：找到至少 {instructions['expected_count']} 个相关URL")
        print("\n" + instructions["instructions"])

        print("\n" + "=" * 60)
        print("💡 使用提示")
        print("=" * 60)
        print("""
1. 在Claude Code中，让AI助手执行上述搜索查询
2. 对每个搜索结果，让AI助手：
   - 识别知乎/V2EX的链接
   - 评估标题的相关性
   - 估计讨论热度

3. 让AI助手整理成JSON格式，保存到：
   data/discovered_urls.json

4. 然后运行：
   python ai_search_helper.py review
   """)

    def run_review(self, discovered_file: Path = None):
        """审核发现的URL"""
        if discovered_file is None:
            discovered_file = PROJECT_ROOT / "data" / "discovered_urls.json"

        if not discovered_file.exists():
            logger.error(f"未找到发现文件: {discovered_file}")
            logger.info("请先运行: python ai_search_helper.py discover")
            return

        logger.info(f"加载发现的URL: {discovered_file}")
        data = load_json(discovered_file)

        urls = data.get("urls", [])
        logger.info(f"共发现 {len(urls)} 个URL")

        # 生成配置模板
        output_dir = PROJECT_ROOT / "data"
        template_file = output_dir / "target_urls_template.json"

        self.discoverer.generate_target_config_template(urls, template_file)

        logger.success("\n" + "=" * 60)
        logger.success("✅ 配置模板已生成")
        logger.success("=" * 60)
        logger.success(f"文件位置: {template_file}")
        logger.success("\n下一步:")
        logger.success("1. 打开模板文件")
        logger.success("2. 访问每个URL，确认相关性和评论数")
        logger.success("3. 填写标题、日期和相关性说明")
        logger.success("4. 将manual_checked改为true")
        logger.success("5. 复制到 config/target_urls.json")
        logger.success("6. 运行: python main.py scrape")

    def run_evaluation(self, data_file: Path = None):
        """评估已采集数据的相关性"""
        logger.info("=" * 60)
        logger.info("📊 相关性评估")
        logger.info("=" * 60)

        # 加载数据
        if data_file is None:
            # 查找最新的数据文件
            from config.config import RAW_DATA_DIR

            raw_files = list(RAW_DATA_DIR.glob("posts_*.json"))
            if not raw_files:
                logger.error("未找到数据文件")
                return
            data_file = max(raw_files, key=lambda p: p.stat().st_mtime)

        logger.info(f"评估数据: {data_file}")
        posts = load_json(data_file)

        # 评估
        scores = self.evaluator.batch_evaluate(posts, method="simple")

        # 生成报告
        report = self.evaluator.generate_evaluation_report(scores)
        print(report)

        # 保存报告
        report_dir = PROJECT_ROOT / "data" / "reports"
        report_file = (
            report_dir
            / f"relevance_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        report_file.write_text(report, encoding="utf-8")

        logger.success(f"评估报告已保存: {report_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI搜索助手 - 自动发现和评估相关讨论",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python ai_search_helper.py discover               # 开始AI辅助搜索
  python ai_search_helper.py review                 # 审核发现的URL
  python ai_search_helper.py evaluate               # 评估已采集数据

Perplexity Sonar模式（需要API密钥）:
  python ai_search_helper.py discover --perplexity --api-key YOUR_KEY
        """,
    )

    parser.add_argument(
        "command", choices=["discover", "review", "evaluate"], help="执行的命令"
    )

    parser.add_argument(
        "--perplexity", action="store_true", help="使用Perplexity Sonar搜索"
    )

    parser.add_argument("--api-key", type=str, help="Perplexity API密钥")

    parser.add_argument("-f", "--file", type=Path, help="指定数据文件路径")

    args = parser.parse_args()

    # 创建应用实例
    app = AISearchHelper(args.perplexity, args.api_key)

    try:
        if args.command == "discover":
            app.run_discovery()
        elif args.command == "review":
            app.run_review(args.file)
        elif args.command == "evaluate":
            app.run_evaluation(args.file)
    except KeyboardInterrupt:
        logger.warning("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
