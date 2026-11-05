from loguru import logger

from ecoinvent_migrate.utils import configure_logs


def test_configure_logs_level(capsys):
    configure_logs(write_logs=False, log_level="WARNING")
    logger.info("hidden message")
    logger.warning("shown message")
    err = capsys.readouterr().err
    assert "hidden message" not in err
    assert "shown message" in err


def test_configure_logs_default_level(capsys):
    configure_logs(write_logs=False)
    logger.info("info message")
    assert "info message" in capsys.readouterr().err
