import os
from pathlib import Path
from typing import List, Union

import yaml

from avaris.api.models import Compendium
from avaris.config.config_loader import ConfigLoader
from avaris.config.error import ConfigError
from avaris.defaults import Defaults
from avaris.utils.logging import get_logger

logger = get_logger()


class ConfigManager:

    def __init__(self, compendium_config_dir: Union[Path, List[Path]] = None) -> None:
        # Initialize compendium_config_dirs as an empty list to handle None case
        self.compendium_config_dirs: List[Path] = []

        if isinstance(compendium_config_dir, Path):
            # If compendium_config_dir is a single Path object, add it to the list
            self.compendium_config_dirs.append(compendium_config_dir)
        elif isinstance(compendium_config_dir, list):
            # If it's a list, extend compendium_config_dirs with non-None values
            self.compendium_config_dirs.extend(
                [d for d in compendium_config_dir if d is not None]
            )
        elif compendium_config_dir is None:
            # If compendium_config_dir is None, use the default directory
            self.compendium_config_dirs.append(Defaults.DEFAULT_COMPENDIUM_DIR)

        self.ensure_files()

    def ensure_files(self) -> None:
        # Filter out None values before attempting to make directories
        self.compendium_config_dirs = [
            d for d in self.compendium_config_dirs if d is not None
        ]
        for directory in self.compendium_config_dirs:
            directory.mkdir(parents=True, exist_ok=True)

    def get_all_config_files(self) -> List[Path]:
        """Get a list of all YAML configuration files in the compendium_config_dirs."""
        all_files = []
        for directory in self.compendium_config_dirs:
            all_files += list(directory.glob("*.yaml")) + list(directory.glob("*.yml"))
        return all_files

    def get_valid_compendium(self) -> List[Compendium]:
        configs: List[Compendium] = []
        for compendium_path in self.get_all_config_files():
            try:
                loaded_config = ConfigLoader.load_compendium_config(compendium_path)
                configs.extend(loaded_config)
            except ConfigError as e:
                logger.error(f"Compendium error from {compendium_path}: {e}")
            except Exception as e:  # Generic catch-all for unexpected errors
                logger.error(f"Unexpected error from {compendium_path}: {e}")
        logger.debug(f"Loaded compendium: {configs}")
        return configs

    def read_config(self, compendium_path: str):
        with open(compendium_path, "r") as file:
            config = yaml.safe_load(file)
        return config
