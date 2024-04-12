from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, HttpUrl, SecretStr, root_validator, validator, ValidationError, ConfigDict

from avaris.defaults import Defaults, Names
from avaris.registry import task_registry
from avaris.utils.logging import get_logger
logger = get_logger()

class ServiceConfig(BaseModel):
    enabled: bool = False

class DataSourceServiceConfig(ServiceConfig):
    type: str = "default"
    port: int = 5000
    listen: bool = False


class Services(BaseModel):
    datasource: Optional[DataSourceServiceConfig] = None
    # Example validator to provide a default instance if the service is None
    @validator("datasource", pre=True, always=True)
    def default_datasource(cls, v):
        return v or DataSourceServiceConfig()

class DataBackendConfig(BaseModel):
    backend: str




class SQLConfig(DataBackendConfig):
    backend: str = Names.SQLITE
    database_url: Optional[str] = Defaults.DEFAULT_SQLITE_PATH


class S3Config(DataBackendConfig):
    backend: str = Names.S3
    rgw_endpoint: str = Field(default="s3://localhost:9000")


class AppConfig(BaseModel):
    execution_backend: str
    data_backend: Union[S3Config, SQLConfig]
    services: Optional[Services] = Services()

    model_config = ConfigDict(extra='ignore')

    @validator("data_backend", pre=True)
    def set_data_backend(cls, v: dict):
        if v.get("backend") == Names.S3:
            return S3Config(**v)
        elif v.get("backend") == Names.SQLITE:
            return SQLConfig(**v)
        else:
            raise ValueError("Unsupported backend")


class OutputConfig(BaseModel):
    type: str  # e.g., "console", "file"
    format: str  # e.g., "json", "text"
    filename: Optional[str] = Field(None, description="Required if type is 'file'.")

    model_config = ConfigDict(extra='ignore')


class ExecutionResult(BaseModel):
    name: str
    task: str
    id: str
    timestamp: datetime
    result: Optional[dict] = None


class BaseParameter(BaseModel):
    __NAME__: str
    model_config = ConfigDict(extra='ignore')
class TaskExecutorConfig(BaseModel):
    task: str
    parameters: Optional[BaseParameter] = None
    secrets: Optional[Dict[str, Optional[SecretStr]]] = None
    model_config = ConfigDict(extra='ignore')

    @validator("parameters", pre=True, always=True)
    def set_parameters(cls, v, values, **kwargs):
        task_type = values.get("task")
        if task_type and task_type in task_registry:
            executor_class = task_registry[task_type]
            parameters_model = executor_class.PARAMETER_TYPE
            try:
                # Ensure v is not None by providing an empty dict if necessary
                parameters_data = v or {}
                return parameters_model(**parameters_data)
            except ValidationError as e:
                logger.warning(
                    f"Parameter validation error for task {task_type}: {e}")
                return None  # Return None or an empty instance of parameters_model
        else:
            raise ValueError(
                f"Unsupported task type: {task_type}. Did it register?")

class TaskConfig(BaseModel):
    name: Optional[str] = None
    schedule: str
    output: Optional[OutputConfig] = None  # Initially None ?
    executor: TaskExecutorConfig
    model_config = ConfigDict(extra='ignore')


class Compendium(BaseModel):
    name: Optional[str] = None
    tasks: List[TaskConfig] = []
    model_config = ConfigDict(extra='ignore')

    @validator('tasks', pre=True)
    def validate_tasks(cls, v):
        validated_tasks = []
        for task_data in v:
            try:
                # Attempt to create a TaskConfig instance for each task
                task = TaskConfig(**task_data)
                validated_tasks.append(task)
            except ValidationError as e:
                # Log the validation error and continue to the next task
                task_name = task_data.get('name', '') if isinstance(task_data, dict) else 'unknown'
                logger.warning(f"Validation error in task '{task_name}': {e}")
        return validated_tasks

class CompendiumWrapper(BaseModel):
    compendium: List[Compendium]

    # Custom validator to ensure compendium is always a list
    @validator("compendium", pre=True)
    def ensure_list(cls, v):
        if isinstance(v, dict):  # Single compendium case
            return [v]  # Wrap it in a list
        return v  # It's already a list



class ListenerData(BaseModel):
    body: dict
    header: dict
