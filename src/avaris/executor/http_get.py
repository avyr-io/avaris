from avaris.executor.executor import TaskExecutor
from pydantic import SecretStr
from avaris.api.models import BaseParameter
from typing import Optional, Literal
from avaris.task.task_registry import register_task_executor
import httpx

class HTTPGetParameters(BaseParameter):
    __NAME__ = 'http_get'
    url: str
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    response_format: Literal['json', 'text',
                             'binary'] = 'text'

@register_task_executor(HTTPGetParameters)
class HTTPGetExecutor(TaskExecutor[HTTPGetParameters]):
    async def execute(self) -> dict:
        try:
            if not self.parameters.url:
                raise ValueError("URL not provided.")

            self.logger.info(f"Fetching data from URL: {self.parameters.url}")
            auth = None
            if self.parameters.username:
                if not self.parameters.password:
                    raise ValueError("Password not provided.")

                auth = httpx.BasicAuth(self.parameters.username, self.parameters.password.get_secret_value())
            async with httpx.AsyncClient() as client:
                response = await client.get(url=self.parameters.url, auth=auth,follow_redirects=True,timeout=60)
                response.raise_for_status()
                self.parameters.response_format = self.parameters.response_format.strip(
                )
                if self.parameters.response_format == 'json':
                    try:
                        data = response.json()
                    except ValueError:
                        self.logger.error(f"Failed to parse JSON from response at {self.parameters.url}")
                        raise
                elif self.parameters.response_format == 'text':
                    data = response.text
                elif self.parameters.response_format == 'binary':
                    data = response.content
                else:
                    self.logger.error(f"Unsupported response format: {self.parameters.response_format}")
                    raise ValueError("Unsupported response format")

                return {'data': data}
        except httpx.HTTPStatusError as http_error:
            error_message = f"HTTP error occurred: {http_error.response.status_code} - {http_error.response.text}"
            self.logger.error(error_message)
            raise
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            raise
