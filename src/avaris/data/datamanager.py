from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger
from typing import Any, List, Optional
from avaris.api.models import ExecutionResult
from avaris.utils.logging import get_logger


class DataManager(ABC):

    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or get_logger()

    @abstractmethod
    async def add_task_result(self, execution_result: ExecutionResult) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def get_filtered_tasks(self, **kwargs):
        raise NotImplementedError()


    @abstractmethod
    async def get_task_result(self, job_id: str) -> ExecutionResult:
        raise NotImplementedError()

    @abstractmethod
    async def get_all_tasks(self) -> List[ExecutionResult]:
        raise NotImplementedError()

    @abstractmethod
    async def get_slice(self, from_time: datetime,
                        to_time: datetime) -> List[ExecutionResult]:
        raise NotImplementedError()

    @abstractmethod
    async def get_all_task_names(self) -> List[str]:
        """
        Fetches a list of unique task names from the database.

        Returns:
            List[str]: A list of unique task names.
        """
        pass
