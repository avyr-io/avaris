from abc import ABC, abstractmethod
from typing import Callable, Generic, Optional, TypeVar
from typing import Dict
from pydantic import BaseModel, SecretStr
import os
from avaris.api.models import ExecutionResult, TaskConfig
from avaris.handler.handler import ResultHandler
from avaris.utils.logging import get_logger
from avaris.utils.parse import get_current_time_in_timezone
from avaris.config.value_parser import ConfigValueParser

T = TypeVar("T", bound=BaseModel)  # Bound T to BaseModel for type safety.

class TaskExecutor(ABC, Generic[T]):
    # Static typing safety check
    PARAMETER_TYPE = TypeVar("PARAMETER_TYPE", bound=BaseModel)
    def __init__(self,
                 task_config: TaskConfig,
                 result_handler: Optional[ResultHandler] = None):
        self.task_config: TaskConfig = task_config
        self.result_handler: ResultHandler = result_handler
        self.logger = get_logger()

        parsed_parameters = {}
        # Use .dict() method to iterate through Pydantic model fields correctly
        for param_key, param_value in self.task_config.executor.parameters.model_dump(
        ).items():
            if isinstance(param_value, str):  # Only parse string values
                parsed_value = ConfigValueParser.parse_value(param_value)
                parsed_parameters[param_key] = parsed_value
            elif isinstance(param_value, SecretStr):
                parsed_value = ConfigValueParser.parse_value(param_value.get_secret_value())
                parsed_parameters[param_key] = SecretStr(parsed_value)
            else:
                parsed_parameters[param_key] = param_value

        # Assuming the parsed_parameters can be directly assigned to self.parameters
        # If T is a Pydantic model, you might need to instantiate T from parsed_parameters
        self.parameters: T = self.PARAMETER_TYPE(
            **parsed_parameters) if issubclass(
                self.PARAMETER_TYPE, BaseModel) else parsed_parameters

    @abstractmethod
    async def execute(self) -> dict:
        raise NotImplementedError


    async def load_secrets(self) -> Dict[str, SecretStr]:
        """Returns task specific secrets as a dictionary.
        Checks environment variables if they were not specified in the configuration

        Returns:
            Dict[str, SecretStr]: _description_
        """
        if not self.task_config.executor.secrets:
            return {}
        loaded_secrets = {}
        for secret_key, secret_config_value in self.task_config.executor.secrets.items(
        ):
            secret_value = secret_config_value or os.environ.get(secret_key, "")
            if not secret_value:
                self.logger.warning(f"Secret {secret_key} not found.")
            # Ensure the secret value is wrapped in SecretStr, if not already
            loaded_secrets[secret_key] = SecretStr(
                str(secret_value)) if not isinstance(secret_value,
                                                    SecretStr) else secret_value
        return loaded_secrets

    def get_task(self, job_id: str) -> Callable:
        """Returns a callable task for scheduling, with result handling integrated."""

        async def task_wrapper() -> ExecutionResult:
            self.logger.info(f"Executing task {self.task_config.name} : {self.task_config.executor.task}")
            result_model = ExecutionResult(
                name=self.task_config.name,
                task=self.task_config.executor.task,
                result={},
                id=job_id,
                timestamp=get_current_time_in_timezone(),
            )  # Initialize result model with empty result dict
            try:
                result = await self.execute()
                result_model = ExecutionResult(
                    name=self.task_config.name,
                    task=self.task_config.executor.task,
                    result=result,
                    id=job_id,
                    timestamp=get_current_time_in_timezone(),
                )
                self.logger.info(
                    f"Task '{self.task_config.name}:{self.task_config.executor.task}' completed successfully"
                )
                if self.result_handler:
                    # Ensure the result handler's handle_result method is awaited
                    await self.result_handler.handle_result(result_model)
            except Exception as e:
                result_model = ExecutionResult(
                    name=self.task_config.name,
                    task=self.task_config.executor.task,
                    result={
                        "error": str(e)
                    },  # This would be an exception, task exec failures still go to the top block because it's caught
                    id=job_id,
                    timestamp=get_current_time_in_timezone(),
                )
                self.logger.error(
                    f"Task '{self.task_config.name}:{self.task_config.executor.task}' failed with error: {str(e)}"
                )
                if self.result_handler:
                    # Pass the error to the result handler in a structured manner
                    await self.result_handler.handle_result(result_model)
            return result_model

        return task_wrapper
