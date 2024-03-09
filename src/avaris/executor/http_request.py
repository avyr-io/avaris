import requests
from pydantic import BaseModel

from avaris.executor.executor import TaskExecutor
from avaris.task.task_registry import register_task_executor


class HttpRequestParameters(BaseModel):
    __NAME__ = "http_request"
    url: str
    method: str

@register_task_executor(HttpRequestParameters.__NAME__)
class HttpExecutor(TaskExecutor[HttpRequestParameters]):
    PARAMETER_TYPE = HttpRequestParameters

    async def execute(self) -> dict:
        try:
            response = requests.get(self.parameters.url)
            if response.status_code == 200:
                return {
                    response: f"Failed to fetch data from {url}. Status code: {response.text}"
                }
            else:
                self.logger.error(
                    f"Failed to fetch {self.parameters.url}: Status {response.status_code}"
                )
                return {}
        except Exception as e:
            self.logger.error(f"Failed to fetch {self.parameters.url}: {e}")
            return {"error": f"Failed to fetch {self.parameters.url}: {e}"}
