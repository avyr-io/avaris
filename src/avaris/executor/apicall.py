import aiohttp
from avaris.executor.executor import TaskExecutor
from avaris.api.models import BaseParameter
from pydantic import HttpUrl
from avaris.task.task_registry import register_task_executor


# Define the task executor configuration
class APICallExecutorParameters(BaseParameter):
    __NAME__ = "api_call"
    url: HttpUrl
    method: str = 'GET'


@register_task_executor(APICallExecutorParameters)
class APICallExecutor(TaskExecutor[APICallExecutorParameters]):
    async def execute(self):
        url = self.parameters.url
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "error":
                        f"Failed to fetch data. Status code: {response.status}"
                    }
