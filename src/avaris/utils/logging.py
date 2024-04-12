import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from avaris.defaults import Defaults
from colorlog import ColoredFormatter

# Global logger variable
logger = None


def init_logging():
    global logger
    if logger is None:
        debug_mode = os.getenv("DEBUG", "").lower() in ["true", "1"]
        logger_name = os.getenv("LOGGER_NAME", "avaris")
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)



        formatter = ColoredFormatter(
            fmt=(
                "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:\033[97m%(lineno)d\033[0m - \033[97m%(message)s\033[0m"
                if debug_mode
                else "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - \033[97m%(message)s\033[0m"
            ),
            datefmt=None,  # You can specify your date format here
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={},
            style="%",
        )

        # Handler for printing logs to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Adjusted formatter to include module names

        console_handler.setFormatter(formatter)

        # Adding both handlers to the logger
        if debug_mode:

            log_file_path = Defaults.DEFAULT_LOG_FILE

            # Handler for writing logs to a file
            file_handler = RotatingFileHandler(
                filename=str(log_file_path), maxBytes=10000000, backupCount=5
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            logger.addHandler(file_handler)
        logger.addHandler(console_handler)


def get_logger(module_name=None):
    if logger is None:
        init_logging()
    if module_name:
        return logging.getLogger(f"{os.getenv('LOGGER_NAME', 'avaris')}.{module_name}")
    return logger
