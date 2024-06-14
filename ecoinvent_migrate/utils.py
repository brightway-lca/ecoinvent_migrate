import datetime
import sys
from pathlib import Path

from loguru import logger
from platformdirs import user_log_dir


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
