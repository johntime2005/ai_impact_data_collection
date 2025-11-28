"""
文件处理模块 - 高性能文件读写

使用orjson（Rust实现）处理JSON，比标准库快数倍
使用polars处理结构化数据，比pandas快很多
"""
import orjson
from pathlib import Path
from typing import Any, Dict, List, Union
from loguru import logger

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    logger.warning("Polars未安装，Parquet功能不可用")


def save_json(
    data: Union[Dict, List],
    file_path: Union[str, Path],
    pretty: bool = False,
    ensure_ascii: bool = False
) -> None:
    """
    保存JSON文件（使用orjson，性能优异）

    Args:
        data: 要保存的数据
        file_path: 文件路径
        pretty: 是否格式化输出
        ensure_ascii: 是否转义非ASCII字符
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # 配置orjson选项
    options = 0
    if pretty:
        options |= orjson.OPT_INDENT_2
    if not ensure_ascii:
        options |= orjson.OPT_NON_STR_KEYS

    # 序列化并写入
    json_bytes = orjson.dumps(data, option=options)
    file_path.write_bytes(json_bytes)

    logger.debug(f"JSON文件已保存: {file_path}")


def load_json(file_path: Union[str, Path]) -> Union[Dict, List]:
    """
    加载JSON文件（使用orjson）

    Args:
        file_path: 文件路径

    Returns:
        解析后的数据
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    json_bytes = file_path.read_bytes()
    data = orjson.loads(json_bytes)

    logger.debug(f"JSON文件已加载: {file_path}")
    return data


def save_to_parquet(
    data: List[Dict],
    file_path: Union[str, Path],
    compression: str = "zstd"
) -> None:
    """
    保存为Parquet格式（使用polars，高性能列式存储）

    Args:
        data: 数据列表（字典列表）
        file_path: 文件路径
        compression: 压缩方式（zstd/snappy/gzip/lz4/uncompressed）

    Raises:
        ImportError: polars未安装
    """
    if not POLARS_AVAILABLE:
        raise ImportError("需要安装polars: pixi add polars")

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # 转换为polars DataFrame
    df = pl.DataFrame(data)

    # 保存为parquet
    df.write_parquet(
        file_path,
        compression=compression,
        use_pyarrow=False  # 使用polars自己的实现
    )

    logger.debug(f"Parquet文件已保存: {file_path} (行数: {len(df)}, 列数: {len(df.columns)})")


def load_from_parquet(file_path: Union[str, Path]) -> pl.DataFrame:
    """
    从Parquet文件加载数据（使用polars）

    Args:
        file_path: 文件路径

    Returns:
        polars DataFrame

    Raises:
        ImportError: polars未安装
        FileNotFoundError: 文件不存在
    """
    if not POLARS_AVAILABLE:
        raise ImportError("需要安装polars: pixi add polars")

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    df = pl.read_parquet(file_path, use_pyarrow=False)

    logger.debug(f"Parquet文件已加载: {file_path} (行数: {len(df)}, 列数: {len(df.columns)})")
    return df


def save_posts_batch(
    posts: List[Dict],
    output_dir: Union[str, Path],
    format: str = "json"
) -> Path:
    """
    批量保存帖子数据

    Args:
        posts: 帖子列表
        output_dir: 输出目录
        format: 保存格式（json/parquet）

    Returns:
        保存的文件路径
    """
    from datetime import datetime

    output_dir = Path(output_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format == "json":
        file_path = output_dir / f"posts_{timestamp}.json"
        save_json(posts, file_path, pretty=True)
    elif format == "parquet":
        file_path = output_dir / f"posts_{timestamp}.parquet"
        save_to_parquet(posts, file_path)
    else:
        raise ValueError(f"不支持的格式: {format}")

    logger.info(f"批量保存完成: {file_path} ({len(posts)} 条记录)")
    return file_path
