from pathlib import Path
import yaml
from typing import List
from avaris.config.config_loader import ConfigLoader  # Assuming this correctly loads & validates YAML
import os
from avaris.api.models import ScraperConfig
from pydantic import ValidationError
from avaris.config.error import MissingScraperKeyError, ConfigError
from avaris.utils.logging import get_logger

logger = get_logger()


class ConfigManager:

    def __init__(self, scraper_config_dir: Path = None) -> None:
        self.scraper_config_dir: Path = scraper_config_dir or Path(
            os.getenv('CONFIG', 'config'))
        self.scraper_config_dir: Path = scraper_config_dir or Path(
            os.getenv('CONFIG', 'config'))
        self.ensure_files()

    def ensure_files(self) -> None:
        self.scraper_config_dir.mkdir(parents=True, exist_ok=True)

    def get_all_config_files(self) -> List[Path]:
        """Get a list of all YAML configuration files in the scraper_config_dir."""
        return list(self.scraper_config_dir.glob('*.yaml')) + list(
            self.scraper_config_dir.glob('*.yml'))

    def get_valid_scrapers(self) -> List[ScraperConfig]:
        configs: List[ScraperConfig] = []
        for config_path in self.get_all_config_files():
            try:
                loaded_config = ConfigLoader.load_scraper_config(config_path)
                configs.extend(loaded_config)
            except MissingScraperKeyError as e:
                logger.info(f"Ignoring {config_path}: {e.message}")
            except ConfigError as e:
                logger.error(
                    f"Configuration error in config from {config_path}: {e}")
            except Exception as e:  # Generic catch-all for unexpected errors
                logger.error(
                    f"Unexpected error in config from {config_path}: {e}")
        logger.debug(f"Loaded configurations: {configs}")
        return configs

    def read_config(self, config_path: str):
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        return config
