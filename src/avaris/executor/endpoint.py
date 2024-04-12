from typing import Any, Dict, Optional

import aiohttp
from pydantic import HttpUrl
from avaris.api.models import BaseParameter

from avaris.executor.executor import TaskExecutor
from avaris.task.task_registry import register_task_executor


class EndpointExecutorParameters(BaseParameter):
    __NAME__ = "endpoint"
    url: HttpUrl
    headers: Dict[str, str] = {}
    params: Optional[Dict[str, Any]] = None
    auth: Optional[Dict[str, str]] = None


@register_task_executor(EndpointExecutorParameters)
class EndpointTaskExecutor(TaskExecutor[EndpointExecutorParameters]):
    async def execute(self) -> dict:
        url = self.parameters.url
        headers = self.parameters.headers
        params = self.parameters.params
        auth = self.parameters.auth
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=headers, params=params, auth=auth
            ) as response:
                self.logger.info(
                    f"Requested URL: {url} with params: {params} got response status {response.status}"
                )
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, dict):
                        return data
                    else:
                        return {"response": data}
                else:
                    self.logger.error(
                        f"Failed to fetch data from {url}. Status code: {response.status}"
                    )
                    raise