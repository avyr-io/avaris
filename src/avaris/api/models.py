from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, HttpUrl, SecretStr, root_validator, validator

from avaris.defaults import Defaults, Names
from avaris.registry import task_registry


class ServiceConfig(BaseModel):
    enabled: bool
    port: int = Field(default=5000)


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
    services: Dict[str, ServiceConfig] = {}

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


class ExecutionResult(BaseModel):
    name: str
    task: str
    id: str
    timestamp: datetime
    result: Optional[dict] = None


class TaskExecutorConfig(BaseModel):
    task: str
    parameters: Optional[BaseModel] = None
    secrets: Optional[Dict[str, Optional[SecretStr]]] = None

    @validator("parameters", pre=True, always=True)
    def set_parameters(cls, v, values, **kwargs):
        task_type = values.get("task")
        if task_type and task_type in task_registry:
            executor_class = task_registry[task_type]
            parameters_model = executor_class.PARAMETER_TYPE
            return parameters_model(**v)
        else:
            raise ValueError(f"Unsupported task type: {task_type}, did it register?")


class TaskConfig(BaseModel):
    name: Optional[str] = None
    schedule: str
    output: Optional[OutputConfig] = None  # Initially None ?
    executor: TaskExecutorConfig


class Compendium(BaseModel):
    destination: Optional[Union[HttpUrl, str]] = None
    name: Optional[str] = None
    tasks: List[TaskConfig]


class CompendiumWrapper(BaseModel):
    compendium: List[Compendium]

    # Custom validator to ensure compendium is always a list
    @validator("compendium", pre=True)
    def ensure_list(cls, v):
        if isinstance(v, dict):  # Single compendium case
            return [v]  # Wrap it in a list
        return v  # It's already a list
