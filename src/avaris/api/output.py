from avaris.api.models import OutputConfig
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field, validator


class datasourceOutputConfig(BaseModel):
    type: str = "datasource"
    dataSourceType: str  # e.g., "prometheus", "graphite", "custom_api"
    dataSourceName: str  # Name of the datasource DataSource
    endpoint: Optional[HttpUrl] = Field(
        None, description="Endpoint for custom API DataSource.")
    auth: Optional[dict] = Field(
        None, description="Authentication details, if required.")
