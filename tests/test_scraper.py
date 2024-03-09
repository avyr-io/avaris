import pytest
from pathlib import Path
from avaris.api.models import ScraperConfig
from avaris.config.config_loader import ConfigLoader
from pydantic import ValidationError


# Define a fixture for loading test data paths
@pytest.fixture
def config_path(tmp_path) -> Path:
    # Create a temporary YAML file for testing
    test_config = tmp_path / "test_config.yml"
    test_config.write_text("""
scrapers:
  - name: "test_scraper"
    destination: "http://example.com"
    tasks:
      - name: "test_task"
        schedule: "0 * * * *"
        output:
          type: "console"
          format: "text"
""")
    return test_config


def test_load_and_validate_config(config_path):
    # Attempt to load the configuration using the ConfigLoader
    configs = ConfigLoader.load_config(config_path)
    print(configs)
    # Ensure that the returned object is a list of ScraperConfig instances
    assert isinstance(configs, list)
    assert all(isinstance(config, ScraperConfig) for config in configs)

    # Validate
