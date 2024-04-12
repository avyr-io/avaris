import subprocess

from avaris.api.models import BaseParameter
from avaris.executor.executor import TaskExecutor
from avaris.task.task_registry import register_task_executor


class ShellExecutorParameters(BaseParameter):
    __NAME__: str = "shell"
    command: str


@register_task_executor(ShellExecutorParameters)
class ShellTaskExecutor(TaskExecutor[ShellExecutorParameters]):
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
            raise
