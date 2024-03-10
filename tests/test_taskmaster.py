from logging import Logger
from typing import Dict, List, Type
from unittest.mock import Mock, create_autospec

import pytest

from avaris.api.models import Compendium, TaskConfig
from avaris.task.taskmaster import ResultHandler, TaskExecutor, TaskMaster
from avaris.utils.logging import get_logger

logger = get_logger()


# A concrete class to test the abstract TaskMaster
class DummyTaskMaster(TaskMaster):
    def get_jobs(self):
        pass

    def remove_job(self, job_id: str):
        pass

    def schedule_job(self, func, job_id: str, schedule: str):
        pass

    def clear_invalid_jobs(self):
        pass

    def create_scheduler(self):
        return Mock()

    def start_scheduler(self):
        pass

    def stop_scheduler(self):
        pass


@pytest.fixture
def task_registry() -> Dict[str, Type[TaskExecutor]]:
    return {"dummy_task": Mock(spec=TaskExecutor)}


@pytest.fixture
def logger() -> Logger:
    return create_autospec(Logger)


@pytest.fixture
def result_handler() -> ResultHandler:
    return create_autospec(ResultHandler)


@pytest.fixture
def task_master(
    task_registry: Dict[str, Type[TaskExecutor]],
    logger: Logger,
    result_handler: ResultHandler,
) -> DummyTaskMaster:
    return DummyTaskMaster(task_registry, logger, result_handler)


def test_init(
    task_master: TaskMaster, task_registry, logger, result_handler: ResultHandler
):
    assert task_master.task_registry == task_registry
    assert task_master.logger is logger
    assert task_master.result_handler is result_handler
    assert not task_master.__running__
    logger.info.assert_called_once()


def test_validate(task_master: DummyTaskMaster) -> None:
    task_list: List[Compendium] = [Mock(spec=Compendium) for _ in range(2)]
    assert task_master.validate(task_list)


def test_reconfigure_active_jobs_empty_list(task_master: DummyTaskMaster) -> None:
    success, message = task_master.reconfigure_active_jobs([])
    assert not success
    assert message == "No valid configurations found."


def test_reconfigure_active_jobs_success(task_master: DummyTaskMaster) -> None:
    task_list: List[Compendium] = [Mock(spec=Compendium) for _ in range(2)]
    success, message = task_master.reconfigure_active_jobs(task_list)
    assert success
    assert message == ""


def test_schedule_active(task_master: DummyTaskMaster) -> None:
    compendium_config = Mock(spec=Compendium)
    task_master.active_jobs.append(compendium_config)
    task_master.schedule_active()
    task_master.logger.error.assert_not_called()


def test_reconcile_failure(task_master: DummyTaskMaster) -> None:
    task_master.clear_invalid_jobs.side_effect = Exception("Test exception")
    with pytest.raises(RuntimeError):
        task_master.reconcile()
    task_master.logger.error.assert_called()
