"""
配置文件 - 数据采集基础配置
"""
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = DATA_DIR / "reports"

# 确保目录存在
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 爬虫配置
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

# 请求配置
REQUEST_TIMEOUT = 30  # 请求超时时间（秒）
REQUEST_DELAY_MIN = 2  # 最小请求间隔（秒）
REQUEST_DELAY_MAX = 5  # 最大请求间隔（秒）
MAX_RETRIES = 3  # 最大重试次数

# 数据质量要求
MIN_COMMENTS_PER_POST = 50  # 每个主贴最少评论数（已根据实际情况调整）
MIN_POSTS_REQUIRED = 18  # 最少主贴数量

# 时间段划分（用于分析）
TIME_PERIODS = [
    {"name": "初期冲击", "start": "2022-12-01", "end": "2023-03-31"},
    {"name": "快速发展", "start": "2023-04-01", "end": "2023-09-30"},
    {"name": "技术普及", "start": "2023-10-01", "end": "2024-03-31"},
    {"name": "深度应用", "start": "2024-04-01", "end": "2024-09-30"},
    {"name": "成熟期", "start": "2024-10-01", "end": "2025-03-31"},
    {"name": "当前状态", "start": "2025-04-01", "end": "2025-11-30"},
]

# 关键词配置（用于初筛和相关性判断）
KEYWORDS = {
    "primary": [  # 主关键词（必须包含至少一个）
        "ChatGPT", "GPT", "大模型", "大语言模型", "AI", "人工智能",
        "文心一言", "通义千问", "讯飞星火", "Claude", "Gemini"
    ],
    "secondary": [  # 次关键词（建议包含）
        "程序员", "开发", "工程师", "IT", "技术", "编程",
        "就业", "失业", "岗位", "职位", "工作", "求职",
        "技能", "能力", "学习", "转型"
    ],
    "exclude": [  # 排除关键词
        "招聘广告", "售卖", "推广", "课程售卖"
    ]
}

# 日志配置
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
LOG_FILE = PROJECT_ROOT / "logs" / "scraper_{time}.log"
