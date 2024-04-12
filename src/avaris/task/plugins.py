import importlib
import sys
from pathlib import Path

from avaris.utils.logging import get_logger

logger = get_logger()


class PluginManager:
    @staticmethod
    def import_plugin_modules(plugins_dir: Path):
        # Assuming plugins_dir is already in sys.path
        if plugins_dir not in sys.path:
            print(plugins_dir)
            sys.path.append(str(plugins_dir.absolute()))
            sys.path.append(str((plugins_dir / "src").absolute()))
        for path in plugins_dir.glob("**/*.py"):
            if path.name == "__init__.py" or not path.is_file():
                continue  # Skip if it's __init__.py or if for any reason it's not a file.

            module_path = f"plugins.executor.{path.stem}"
            try:
                # Directly attempt to import the module assuming 'plugins.executor' is correct.
                importlib.import_module(module_path)
                logger.info(f"Successfully imported {module_path}")
            except ModuleNotFoundError as e:
                logger.error(f"Failed to import {module_path}: {e}")
