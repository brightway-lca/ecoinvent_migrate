import datetime
import os
import sys
from pathlib import Path
from typing import Optional

from loguru import logger
from platformdirs import user_data_dir, user_log_dir


def configure_logs(write_logs: bool = True) -> None:
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    if write_logs:
        logs_dir = Path(
            user_log_dir("ecoinvent_migrate", "pylca")
        ) / datetime.datetime.now().isoformat()[:19].replace(":", "-")
        logger.info("Writing logs to {path}", path=logs_dir)
        logs_dir.mkdir(parents=True, exist_ok=True)
        logger.add(logs_dir / "debug.log", level="DEBUG")
        logger.add(logs_dir / "info.log", level="INFO")


def setup_output_directory(output_directory: Optional[Path]) -> Path:
    if output_directory is None:
        output_directory = Path(user_data_dir("ecoinvent_migrate", "pylca"))
        if not output_directory.exists():
            logger.info(f"Creating output directory {output_directory}")
            output_directory.mkdir(parents=True)
    elif not isinstance(output_directory, Path):
        raise ValueError(
            f"`output_directory` must be a `Path` instance; got {type(output_directory)}"
        )
    elif not output_directory.is_dir() or not os.access(output_directory, os.W_OK):
        raise ValueError(f"`output_directory` {output_directory} must be a writable directory")
    return output_directory


def cache_dir() -> Path:
    cache_directory = Path(user_data_dir("ecoinvent_migrate", "pylca")) / "cache"
    if not cache_directory.exists():
        cache_directory.mkdir(parents=True)
    return cache_directory
