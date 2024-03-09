import yaml
from pathlib import Path
from avaris.defaults import Defaults
from avaris.api.models import ScraperConfig
from pydantic import ValidationError
from typing import List, Union
from avaris.config.error import ConfigError, MissingScraperKeyError
from avaris.api.models import AppConfig
from avaris.utils.logging import get_logger

logger = get_logger()

class ConfigLoader:

    @staticmethod
    def load_scraper_config(file_path: Union[str, Path]) -> List[ScraperConfig]:
        with open(file_path, 'r') as file:
            config_data = yaml.safe_load(file)
            # Handle the case where the YAML file is empty or contains only comments
            if config_data is None:
                config_data = {}  # Use an empty dictionary if no data is found

        try:
            if ScraperConfig.__NAME__ in config_data:  # Adjust to match your actual root key
                config_list = config_data[ScraperConfig.__NAME__]
                return [ScraperConfig(**item) for item in config_list]
            else:
                raise MissingScraperKeyError(
                    f"No '{ScraperConfig.__NAME__}' key found in YAML.")
        except ValidationError as e:
            raise ConfigError(f"Invalid configuration in {file_path}: {e}")

    @staticmethod
    def load_global_config(file_path: str) -> AppConfig:
        if file_path:
            # None goes to else block
            if Path(file_path).exists():
                with open(file_path, 'r') as file:
                    config_data = yaml.safe_load(file)
                try:
                    return AppConfig(**config_data)
                except ValidationError as e:
                    raise ConfigError(f"Invalid Avaris configuration in {file_path}: {e}")
            else:
                logger.warning(f"No configuration file found at {file_path}!")
                raise ConfigError(f"No configuration found {file_path}: {e}")
        else:
            logger.warning(f"No configuration file provided {file_path}, using defaults...")
            config_data = yaml.safe_load(Defaults.DEFAULT_CONF)
            return AppConfig(**config_data)