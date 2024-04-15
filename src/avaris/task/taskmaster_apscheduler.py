import asyncio
from logging import Logger
from typing import Callable, Dict, Type

import pytz
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from avaris.executor.executor import TaskExecutor
from avaris.task.taskmaster import TaskMaster
from avaris.utils.logging import get_logger


class APSchedulerTaskMaster(TaskMaster):
    scheduler: AsyncIOScheduler

    def __init__(
        self,
        task_registry: Dict[str, Type[TaskExecutor]],
        logger: Logger = None,
        use_daemon=False,
        result_handler: Callable = None,
    ):
        self.use_daemon = use_daemon
        super().__init__(
            logger=logger, task_registry=task_registry, result_handler=result_handler
        )
        """Create and return a BackgroundScheduler instance."""

    def create_scheduler(self) -> AsyncIOScheduler:
        """Create and return an AsyncIOScheduler instance."""
        executors = {
            "default": ThreadPoolExecutor(10),  # For synchronous tasks
            "asyncio": AsyncIOExecutor(),  # For asynchronous tasks
        }
        job_defaults = {
            "coalesce": False,
            "max_instances": 1,
        }
        scheduler = AsyncIOScheduler(
            executors=executors, job_defaults=job_defaults, timezone="UTC"
        )
        return scheduler

    def start_scheduler(self):
        """Start the APScheduler."""
        self.scheduler.start()

    def stop_scheduler(self):
        """Stop the APScheduler."""
        self.scheduler.shutdown()

    def get_jobs(self):
        """Retrieve all jobs currently scheduled in the APScheduler."""
        return self.scheduler.get_jobs()

    def clear_invalid_jobs(self):
        """Remove all jobs that are no longer active based on unique job IDs."""
        # Generate a set of current job IDs based on the active jobs
        try:
            if len(self.scheduled_job_ids):
                current_job_ids = self.get_job_ids()
                # Retrieve all scheduled job IDs from the scheduler
                scheduled_job_ids = {job.id for job in self.get_jobs()}

                # Determine which jobs are outdated (i.e., scheduled but not in current_job_ids)
                outdated_job_ids = scheduled_job_ids - current_job_ids

                # Remove each outdated job from the scheduler
                for job_id in outdated_job_ids:
                    self.remove_job(job_id)
                    self.logger.info(f"Removed {job_id}.")
            else:
                self.logger.info("No jobs to empty.")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing jobs! {e}")

    def remove_job(self, job_id: str):
        super().remove_job(job_id)  # Call to super if you need common logic
        if job_id in self.scheduled_job_ids:
            self.scheduler.remove_job(job_id)
            self.scheduled_job_ids.remove(job_id)  # Remove from tracking set

    def schedule_job(self, func: Callable, job_id: str, schedule: str):
        trigger = CronTrigger.from_crontab(schedule, timezone=pytz.UTC)

        if asyncio.iscoroutinefunction(func):
            # This is an async function, schedule it with asyncio executor
            self.scheduler.add_job(
                func, trigger, id=job_id, executor="asyncio", replace_existing=True
            )
        else:
            # This is a sync function, schedule as usual
            self.scheduler.add_job(func, trigger, id=job_id, replace_existing=True)
        self.scheduled_job_ids.add(job_id)
