from abc import ABC, abstractmethod
from logging import Logger
from typing import Callable, Dict, List, Optional, Set, Tuple, Type

from avaris.api.models import Compendium, TaskConfig
from avaris.config.error import ConfigError
from avaris.executor.executor import TaskExecutor
from avaris.handler.handler import ResultHandler
from avaris.utils.logging import get_logger
from avaris.utils.parse import generate_task_id, parse_cron_schedule


class TaskMaster(ABC):

    def __init__(
        self,
        task_registry: Dict[str, Type[TaskExecutor]],
        logger: Logger = None,
        result_handler: ResultHandler = None,
    ):
        self.__running__ = False
        self.result_handler: ResultHandler = result_handler
        self.logger: Logger = logger or get_logger()
        self.task_registry: Dict[str, Type[TaskExecutor]] = task_registry

        self.active_jobs: List[Compendium] = []
        self.scheduled_job_ids: Set[str] = set()
        self.scheduler = self.create_scheduler()
        self.logger.info(f"Using {type(self.scheduler).__name__}")

    def validate(self, task_list: List[Compendium]) -> bool:
        active_tasks = [
            task for compendium_config in task_list for task in compendium_config.tasks
        ]
        # TODO: Implement actual validation logic
        return True

    def reconfigure_active_jobs(self, task_list: List[Compendium]) -> Tuple[bool, str]:
        if not task_list:  # If the task list is empty
            return False, "No valid configurations found."

        if self.validate(task_list):
            active_tasks = [
                task.name
                for compendium_config in task_list
                for task in compendium_config.tasks
            ]
            self.logger.info(f"Reconfiguring active jobs: {active_tasks}")
            self.active_jobs = task_list
            return True, ""  # Indicates success with no error message
        else:
            return False, "Validation failed for configurations."

    def get_executor(self, task_config: TaskConfig) -> TaskExecutor:
        if not task_config.executor:
            raise ValueError("TaskConfig missing executor info.")
        executor_class = self.task_registry.get(task_config.executor.task)
        if not executor_class:
            raise ValueError(
                f"No executor registered for type '{task_config.executor.task}'"
            )
        return executor_class(
            task_config=task_config, result_handler=self.result_handler
        )

    def configure_task_for_scheduling(
        self, executor: TaskExecutor, task_config: TaskConfig
    ) -> Optional[Callable]:
        self.logger.debug(
            f"Fetching executor for task {task_config.name}:{task_config.executor.task}"
        )

        task_with_handler = executor.get_task(result_handler=self.result_handler)

        return task_with_handler

    def reconcile(self) -> None:
        try:
            self.clear_invalid_jobs()
            self.schedule_active()
            self.logger.info(f"Reconciliation success")
        except Exception as e:
            self.logger.error(f"Error reconciling : {e}")
            raise RuntimeError(f"Error reconciling : {e}")

    def schedule_active(self):
        # Schedule new and updated jobs from the active_jobs list.
        for compendium_config in self.active_jobs:
            try:
                self.compendium_commit(compendium_config)
            except ValueError as e:
                self.logger.error(f"Error scheduling task: {e}")
                raise ConfigError(f"Error scheduling task: {e}")

    def compendium_commit(self, compendium_config: Compendium) -> None:
        self.logger.info(f"Compendium Commit for: {compendium_config.name}")
        for task_config in compendium_config.tasks:
            executor = self.get_executor(task_config)
            if not executor:
                self.logger.error(f"No executor found for task: {task_config.name}")
                continue
            job_id = generate_task_id(
                compendium_config.name,
                task_config.name,
                task_config.executor.parameters,
            )
            func = executor.get_task(job_id)
            if not func:
                self.logger.warning(
                    f"No function configured for task: {task_config.name}"
                )
                continue
            self.logger.info(
                f"Scheduling task: {task_config.name}:{task_config.executor.task}"
            )

            schedule = (
                task_config.schedule
            )  # Assuming schedule is directly compatible with APScheduler's format

            self.schedule_job(func, job_id, schedule)

    def get_job_ids(self):
        """Generate the set of current job IDs based on the active jobs"""
        return set(
            generate_task_id(
                compendium_config.name,
                task_config.name,
                task_config.executor.parameters,
            )
            for compendium_config in self.active_jobs
            for task_config in compendium_config.tasks
        )

    @abstractmethod
    def get_jobs(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_job(self, job_id: str) -> None:
        # This method should remove the job from the scheduler and the tracking set
        raise NotImplementedError

    @abstractmethod
    def schedule_job(self, func: Callable, job_id: str, schedule: str) -> None:
        # This method should add the job to the scheduler and update the tracking set!
        raise NotImplementedError

    @abstractmethod
    def clear_invalid_jobs(self):
        """
        Create and return a scheduler instance specific to the library being used (Celery, APScheduler, Dask, etc.)
        """
        raise NotImplementedError

    @abstractmethod
    def create_scheduler(self):
        """
        Create and return a scheduler instance specific to the library being used (Celery, APScheduler, Dask, etc.)
        """
        raise NotImplementedError

    @abstractmethod
    def start_scheduler(self):
        """
        Start or resume the scheduler. Implementation depends on the specific scheduler being used.
        """
        raise NotImplementedError

    @abstractmethod
    def stop_scheduler(self):
        """
        Stop or pause the scheduler. The specific method to call depends on the scheduler used.
        """
        raise NotImplementedError

    def start(self):
        """
        Start or resume the scheduler. Implementation depends on the specific scheduler being used.
        """
        if not self.__running__:
            self.logger.info("Starting scheduler")
            self.start_scheduler()
            self.__running__ = True

    def stop(self):
        """
        Stop or pause the scheduler. The specific method to call depends on the scheduler used.
        """
        if self.__running__:
            self.logger.info("Stopping scheduler")
            self.stop_scheduler()
            self.__running__ = False
