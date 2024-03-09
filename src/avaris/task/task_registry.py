from typing import Type
from avaris.executor.executor import TaskExecutor
from functools import wraps
from avaris.utils.logging import get_logger
import avaris.registry as registry

logger = get_logger()


def register_task_executor(executor_type: str):

    def decorator(executor_class: Type[TaskExecutor]):
        logger.debug(f"Registering task executor: {executor_class}")

        @wraps(executor_class)
        def wrapper(*args, **kwargs):
            return executor_class(*args, **kwargs)

        if executor_type in registry.task_registry:
            raise ValueError(
                f"Executor type '{executor_type}' is already registered.")
        registry.task_registry[executor_type] = executor_class
        return executor_class

    return decorator
