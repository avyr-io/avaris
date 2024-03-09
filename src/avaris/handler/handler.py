from avaris.data.datamanager import DataManager
from logging import Logger
from avaris.api.models import ExecutionResult
from avaris.utils.logging import get_logger

from avaris.data.sql import ExecutionResult as DBExecutionResult  # SQLAlchemy model


class ResultHandler:

    def __init__(self, data_manager: DataManager, logger: Logger = None):
        self.logger = logger or get_logger()
        self.data_manager = data_manager

    async def handle_result(self,
                            task_result: ExecutionResult):  # Pydantic model
        self.logger.info(f"Handling task result for task: {task_result.task}")

        await self.data_manager.add_task_result(task_result)
