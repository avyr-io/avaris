from typing import Type
from avaris.executor.executor import TaskExecutor
from avaris.api.models import BaseParameter
import avaris.registry as registry
from avaris.utils.logging import get_logger

logger = get_logger()

def register_task_executor(parameter_model: Type[BaseParameter]):
    """
    A decorator to register task executors along with their parameter model.
    Args:
        parameter_model (Type[BaseModel]): The Pydantic model for task parameters.
    """

    def decorator(executor_class: Type[TaskExecutor]):
        logger.debug(
            f"Registering task executor: {executor_class.__name__} with parameters: {parameter_model.__name__}"
        )

        # Dynamically set the PARAMETER_TYPE attribute on the executor class.
        executor_class.PARAMETER_TYPE = parameter_model

        executor_type = parameter_model.__NAME__
        if executor_type in registry.task_registry:
            raise ValueError(
                f"Executor type '{executor_type}' is already registered.")

        registry.task_registry[executor_type] = executor_class
        return executor_class

    return decorator
