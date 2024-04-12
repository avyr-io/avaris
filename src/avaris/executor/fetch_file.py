from avaris.executor.executor import TaskExecutor
from avaris.task.task_registry import register_task_executor
from avaris.utils.logging import get_logger
import os
import aiofiles
import aiohttp
from avaris.utils.parse import read_from_json, csv_to_json
from pydantic import HttpUrl
from typing import Optional, Dict
from avaris.api.models import BaseParameter

class FetchFileExecutorParameters(BaseParameter):
    __NAME__: str = "fetch"
    url: HttpUrl
    headers: Dict[str, str] = {}
    file_name: str
    file_format: str = "csv"
    auth: Optional[Dict[str, str]] = None

logger = get_logger()

@register_task_executor(FetchFileExecutorParameters)
class FetchFileTaskExecutor(TaskExecutor[FetchFileExecutorParameters]):
    async def fetch_file(self) -> dict:
        url = self.parameters.url
        headers = self.parameters.headers  # This defaults to {} if not provided
        file_name = self.parameters.file_name
        file_format = self.parameters.file_format  # Defaults to "csv" if not provided
        auth = self.parameters.auth  # This is optional and could be None
        os.makedirs('tmp', exist_ok=True)  # Ensure the tmp directory exists

        file_path = os.path.join("tmp", f"{file_name}.{file_format}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers,
                                   auth=auth) as response:
                logger.info(
                    f'Fetching {file_name}.{file_format} from {url} returns {response.status}'
                )
                if response.status == 200:
                    async with aiofiles.open(file_path, "wb") as f:
                        await f.write(await response.read())
                    logger.info(
                        f'{file_name}.{file_format} file downloaded successfully'
                    )
                    if file_format == "csv":
                        csv_to_json(file_path,
                                    file_path.replace(".csv", ".json"))
                        logger.info(
                            f'{file_name}.{file_format} file converted to json successfully'
                        )
                    return read_from_json(file_path.replace(".csv", ".json"))
                else:
                    logger.error(
                        f'Failed to download file from {url}. Status code: {response.status}'
                    )
                    raise
