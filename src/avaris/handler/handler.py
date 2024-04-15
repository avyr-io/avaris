import asyncio
from avaris.data.datamanager import DataManager
from logging import Logger
from avaris.api.models import ExecutionResult
from avaris.utils.logging import get_logger

class ResultHandler:
    def __init__(self, data_manager: DataManager, logger: Logger = None):
        self.logger = logger or get_logger()
        self.data_manager = data_manager
        self.results_queue = asyncio.Queue()
        self.worker_task = asyncio.create_task(self.process_results())

    async def handle_result(self, task_result: ExecutionResult):
        await self.results_queue.put(task_result)
        self.logger.debug(f"Result for {task_result.name}:{task_result.task} queued for processing.")

    async def process_results(self):
        while True:
            task_result = await self.results_queue.get()
            try:
                success = await self.data_manager.add_task_result(task_result)
                if success:
                    self.logger.info(f"Successfully processed result for {task_result.name}:{task_result.task}")
                else:
                    self.logger.error(f"Failed to process result for {task_result.name}:{task_result.task}")
            finally:
                self.results_queue.task_done()
