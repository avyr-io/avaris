import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Global logger variable
logger = None


def init_logging():
    global logger
    if logger is None:
        logger_name = os.getenv("LOGGER_NAME", "avaris")
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        logs_path = Path(os.getenv("LOGS", Path.cwd() / "logs"))
        if not logs_path.is_dir():
            logs_path.mkdir(parents=True, exist_ok=True)
        log_file_path = logs_path / f"{logger_name}.log"

        # Handler for writing logs to a file
        file_handler = RotatingFileHandler(filename=str(log_file_path),
                                           maxBytes=10000000,
                                           backupCount=5)
        file_handler.setLevel(logging.DEBUG)

        # Handler for printing logs to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Adjusted formatter to include module names
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Adding both handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)


def get_logger(module_name=None):
    if logger is None:
        init_logging()
    if module_name:
        return logging.getLogger(
            f"{os.getenv('LOGGER_NAME', 'avaris')}.{module_name}")
    return logger
