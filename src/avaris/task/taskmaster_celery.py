from celery import Celery
from avaris.task.taskmaster import TaskMaster
from avaris.executor.executor import TaskExecutor
from typing import Type, Dict


class CeleryTaskMaster(TaskMaster):

    def __init__(self, celery_app: Celery):
        super().__init__()
        self.scheduler = celery_app

    def schedule_tasks(self, task_registry: Dict[str, Type[TaskExecutor]]):
        for task_name, task_info in task_registry.items():
            self._create_and_register_celery_task(task_name, task_info)

    def _create_and_register_celery_task(self, task_name, task_info):
        executor: TaskExecutor = self.get_executor(
            task_info['function'].__annotations__['return']
        )  # Simplified; adjust as needed

        @self.scheduler.task(name=task_name)
        def celery_task():
            # Adjust to pass correct parameters to execute
            executor.execute(task_info['function'])

    def start(self):
        # Starting a Celery scheduler might involve ensuring the worker is running.
        # Typically handled externally, but can be managed programmatically if needed
        pass

    def stop(self):
        # Gracefully stopping Celery tasks might involve revoking tasks or shutting down workers.
        # This is typically handled via Celery's command-line tools or a management interface
        pass
