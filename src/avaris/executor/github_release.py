import re
import httpx
from pydantic import BaseModel, HttpUrl,SecretStr
from typing import  Optional
from avaris.executor.executor import TaskExecutor
from avaris.task.task_registry import register_task_executor


class GitHubReleaseRequestParameters(BaseModel):
    __NAME__ = "http_get_github_release"
    api_url: HttpUrl
    username: Optional[str] = None
    password: Optional[SecretStr] = None


@register_task_executor(GitHubReleaseRequestParameters.__NAME__)
class GitHubReleaseExecutor(TaskExecutor[GitHubReleaseRequestParameters]):
    PARAMETER_TYPE = GitHubReleaseRequestParameters
    async def execute(self) -> dict:
        try:
            secrets = await self.load_secrets()
            github_token = secrets.get("GITHUB_TOKEN", None)
            headers = {"Accept": "application/vnd.github.v3+json"}

            url = self.parameters.api_url.unicode_string()
            async with httpx.AsyncClient() as client:
                if github_token:
                    headers[
                        "Authorization"] = f"token {github_token.get_secret_value()}"
                    response = await client.get(url,
                                                headers=headers)
                elif self.parameters.username and self.parameters.password:
                    auth = (self.parameters.username,
                            self.parameters.password.get_secret_value())
                    response = await client.get(url,
                                                headers=headers,
                                                auth=auth)
                else:
                    response = await client.get(url,
                                                headers=headers)

            if response.status_code == 200:
                data = response.json()
                version_tag = data.get("tag_name", "").strip(
                    "v")  # Remove leading 'v' if present
                release_date = data.get("published_at",
                                        "").split("T")[0]  # YYYY-MM-DD format

                # Extract repository name
                match = re.search(r"/repos/([^/]+/[^/]+)/releases/latest",
                                  url)
                repository_name = match.group(1) if match else "Unknown"

                return {
                    "name": repository_name,
                    "latest_version": version_tag,
                    "release_date": release_date
                }

            else:
                self.logger.error(
                    f"Failed to fetch {self.parameters.api_url}: Status {response.status_code}"
                )
                return {"error": f"HTTP Error: Status {response.status_code}"}
        except Exception as e:
            self.logger.error(f"Exception during fetch: {str(e)}")
            return {"error": f"Exception: {str(e)}"}
