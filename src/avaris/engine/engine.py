from logging import Logger
from pathlib import Path
from typing import List, Tuple

import yaml

from avaris.api.models import Compendium
from avaris.config.config_manager import ConfigManager
from avaris.data.datamanager import DataManager
from avaris.task.taskmaster import TaskMaster
from avaris.utils.logging import get_logger


class AvarisEngineState:
    STOPPED = "stopped"
    RUNNING = "running"


class AvarisEngine:

    def __init__(
        self,
        data_manager: DataManager,
        task_master: TaskMaster,
        compendium_config_dir: Path = None,
        logger: Logger = None,
    ):
        self.state = AvarisEngineState.STOPPED
        self.compendium_config_dir = compendium_config_dir
        self.logger = logger or get_logger()
        self.task_master = task_master
        self.config_manager = ConfigManager(
            compendium_config_dir=self.compendium_config_dir
        )
        self.data_manager = data_manager
        self.compendium_configs: List[Compendium] = []

    def load_compendium_configs(self) -> Tuple[bool, str]:
        try:
            if self.compendium_config_dir:
                self.compendium_configs = self.config_manager.get_valid_compendium()
                if not self.compendium_configs:
                    self.logger.critical("No valid compendium found.")
                    return False, "No valid compendium"
            else:
                self.logger.warning("No compendium directory specified.")
                return False, "Compendium directory not specified"
            return True, None
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to load or parse compendium: {e}")
            return False, f"YAML Error: {e}"
        except Exception as e:
            self.logger.error(f"Unexpected error loading compendium: {e}")
            return False, f"Unexpected error: {e}"

    def dispatch(self):
        try:
            success, error = self.task_master.reconfigure_active_jobs(
                self.compendium_configs
            )
            if success:
                self.logger.info("Successfully reconfigured tasks.")
                self.task_master.reconcile()
            else:
                self.logger.error(f"Failed to reconfigure tasks: {error}")
                raise Exception("Reconfiguration failed")
        except Exception as e:
            self.logger.error(f"Error dispatching tasks: {e}")
            self.stop()
            raise RuntimeError(f"Error dispatching tasks: {e}")

    async def start(self) -> Tuple[bool, str]:
        if self.state == AvarisEngineState.RUNNING:
            self.logger.info("Avaris is already running.")
            return True, "Already running"
        try:
            validate_success, error = self.load_compendium_configs()
            if validate_success:
                self.dispatch()
            else:
                self.logger.warning(f"Engine start failure: {error}")
                return False, error
            self.task_master.start()
            self.logger.info(
                f"Avaris started with {len(self.compendium_configs)} compendiums and {len(self.task_master.get_job_ids())} tasks commissioned."
            )
            self.state = AvarisEngineState.RUNNING
            return True, "OK"
        except RuntimeError as e:
            raise RuntimeError(f"Error starting engine: {e}")
        except Exception as e:
            self.logger.error(f"Error starting the engine: {e}")
            return False, e

    async def stop(self):
        if self.state == AvarisEngineState.STOPPED:
            self.logger.info("Avaris is already stopped.")
            return
        try:

            self.task_master.stop()
            self.logger.info("Avaris has been stopped.")
            self.state = AvarisEngineState.STOPPED
        except Exception as e:
            self.logger.error(f"Error stopping the engine: {e}")

    async def shutdown(self):
        self.task_master.stop()
        self.state = AvarisEngineState.STOPPED
        self.logger.info("Engine shutdown completed.")
