from pathlib import Path
from typing import List, Union

import yaml
from pydantic import ValidationError

from avaris.api.models import AppConfig, Compendium, CompendiumWrapper
from avaris.config.error import ConfigError
from avaris.defaults import Defaults
from avaris.utils.logging import get_logger

logger = get_logger()


class ConfigLoader:

    @staticmethod
    def load_compendium_config(file_path: Union[str, Path]) -> List[Compendium]:
        with open(file_path, "r") as file:
            config_data = yaml.safe_load(file)
            # Handle the case where the YAML file is empty or contains only comments
            if config_data is None:
                config_data = {}  # Use an empty dictionary if no data is found

        try:
            compendium_wrapper = CompendiumWrapper(**config_data)
            return compendium_wrapper.compendium
        except ValidationError as e:
            raise ConfigError(f"Invalid configuration in {file_path}: {e}")

    @staticmethod
    def load_global_config(file_path: str) -> AppConfig:
        if file_path:
            # None goes to else block
            if Path(file_path).exists():
                with open(file_path, "r") as file:
                    config_data = yaml.safe_load(file)
                try:
                    return AppConfig(**config_data)
                except ValidationError as e:
                    logger.error(f"Invalid Avaris configuration in {file_path}: {e}")
                    raise ConfigError(
                        f"Invalid Avaris configuration in {file_path}: {e}"
                    )
            else:
                logger.warning(f"No configuration file found at {file_path}!")
                raise ConfigError(f"No configuration found {file_path}: {e}")
        else:
            logger.warning(
                f"No configuration file provided{f' {file_path}' if file_path else '.'} Using defaults..."
            )
            config_data = yaml.safe_load(Defaults.DEFAULT_CONF)
            return AppConfig(**config_data)
