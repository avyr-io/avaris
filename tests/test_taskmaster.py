from unittest.mock import Mock, create_autospec, patch
import pytest
from pydantic import BaseModel
from typing import List
from avaris.task.task_registry import register_task_executor
from avaris.registry import task_registry
from avaris.executor.executor import TaskExecutor
from avaris.api.models import TaskConfig, Compendium
from avaris.task.taskmaster import ResultHandler, TaskMaster
from avaris.utils.logging import get_logger
from avaris.config.config_loader import ConfigLoader


@pytest.fixture
def mock_logger():
    with patch('avaris.utils.logging.get_logger') as mock_get_logger:
        yield mock_get_logger.return_value

@pytest.fixture
def mock_executor():
    class MockParameters(BaseModel):
        __NAME__: str = "example_task"

    @register_task_executor(MockParameters.__NAME__)
    class MockExecutor(TaskExecutor[MockParameters]):
        PARAMETER_TYPE = MockParameters

        async def execute(self):
            return {"mock": "result"}


@pytest.fixture
def loaded_compendium(valid_config_path):
    compendium_configs = ConfigLoader.load_compendium_config(valid_config_path)
    return compendium_configs[0]

@pytest.fixture
def valid_config_path(tmp_path):
    config_content = """
    compendium:
      - name: ExampleCompendium
        tasks:
          - name: ExampleTask
            schedule: '0 * * * *'
            output:
              type: 'console'
              format: 'text'
            executor:
              task: 'example_task'
    """
    path = tmp_path / "valid_compendium.yml"
    path.write_text(config_content)
    return path

logger = get_logger()

# Define a mock executor fixture to be used in tests
def test_compendium_creation_from_config(valid_config_path):
    # Load compendium configs from the provided YAML file
    compendium_configs = ConfigLoader.load_compendium_config(valid_config_path)
    assert len(compendium_configs) == 1
    assert compendium_configs[0].name == "ExampleCompendium"

# Dummy TaskMaster for testing abstract behaviors
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
def result_handler() -> ResultHandler:
    return create_autospec(ResultHandler)


@pytest.fixture
def task_master(result_handler: ResultHandler) -> DummyTaskMaster:
    return DummyTaskMaster(task_registry, logger, result_handler)


@patch('avaris.utils.logging.get_logger')
def test_init(mock_get_logger):
    mock_logger = mock_get_logger.return_value
    task_master = DummyTaskMaster(task_registry, mock_logger, result_handler)
    assert not task_master.__running__
    mock_logger.info.assert_called_once()


def test_validate(task_master: DummyTaskMaster):
    task_list: List[Compendium] = [
        Mock(spec=Compendium, tasks=[]) for _ in range(2)
    ]
    assert task_master.validate(task_list)


def test_reconfigure_active_jobs_empty_list(task_master: DummyTaskMaster):
    success, message = task_master.reconfigure_active_jobs([])
    assert not success
    assert message == "No valid configurations found."


def test_reconfigure_active_jobs_success(task_master: DummyTaskMaster,
                                         loaded_compendium):
    task_list: List[Compendium] = [loaded_compendium]
    success, message = task_master.reconfigure_active_jobs(task_list)
    assert success
    assert message == ""


def test_schedule_active(task_master: DummyTaskMaster, loaded_compendium,
                         mock_logger):
    task_master.active_jobs.append(loaded_compendium)
    task_master.schedule_active()
    mock_logger.error.assert_not_called()

def test_reconcile_failure(task_master: DummyTaskMaster):
    with patch.object(task_master,
                      'clear_invalid_jobs',
                      side_effect=Exception("Test exception")):
        with pytest.raises(RuntimeError):
            task_master.reconcile()
