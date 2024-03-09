import subprocess

from pydantic import BaseModel

from avaris.api.models import TaskExecutorConfig
from avaris.executor.executor import TaskExecutor
from avaris.task.task_registry import register_task_executor
from avaris.utils.logging import get_logger


class ShellExecutorParameters(BaseModel):
    __NAME__: str = "shell"
    command: str


@register_task_executor(ShellExecutorParameters.__NAME__)
class ShellTaskExecutor(TaskExecutor[ShellExecutorParameters]):
    PARAMETER_TYPE = ShellExecutorParameters

    async def execute(self):
        # Assuming command is a string; adjust if it's intended to be a list
        command = self.parameters.command
        try:
            result = subprocess.run(
                command,
                shell=True,  # trunk-ignore(bandit/B602)
                capture_output=True,
                text=True,
            )
            self.logger.info(result.stdout)
            return {"stdout": result.stdout, "stderr": result.stderr}
        except Exception as e:
            self.logger.error(f"Task failed with error: {str(e)}")
            return {"error": str(e)}
