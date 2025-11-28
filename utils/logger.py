"""
日志配置模块 - 使用loguru进行日志管理
"""
import sys
from pathlib import Path
from loguru import logger
from typing import Optional


def setup_logger(
    log_file: Optional[Path] = None,
    level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "7 days",
    console: bool = True
) -> None:
    """
    配置全局日志器

    Args:
        log_file: 日志文件路径，None表示只输出到控制台
        level: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
        rotation: 日志文件轮转大小
        retention: 日志文件保留时间
        console: 是否输出到控制台
    """
    # 移除默认handler
    logger.remove()

    # 添加控制台输出
    if console:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            level=level,
            colorize=True
        )

    # 添加文件输出
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=level,
            rotation=rotation,
            retention=retention,
            encoding="utf-8",
            enqueue=True  # 异步写入，提高性能
        )

    logger.info(f"日志系统初始化完成，级别: {level}")


def get_logger(name: str = __name__):
    """
    获取logger实例

    Args:
        name: logger名称

    Returns:
        logger实例
    """
    return logger.bind(name=name)
