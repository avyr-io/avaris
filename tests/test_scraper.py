from pathlib import Path

import pytest
from pydantic import ValidationError

from avaris.api.models import Compendium
from avaris.config.config_loader import ConfigLoader


# Define a fixture for loading test data paths
@pytest.fixture
def config_path(tmp_path) -> Path:
    # Create a temporary YAML file for testing
    test_config = tmp_path / "test_config.yml"
    test_config.write_text(
        """
compendium:
  name: test_compendium
  destination: "http://example.com"
  tasks:
    - name: test_task
      schedule: '0 * * * *'
      output:
        type: "console"
        format: "text"
      executor:
        name: shell
        parameters:
          param1: "value1"
          param2: "value2
"""
    )
    return test_config


def test_load_and_validate_config(config_path):
    # Attempt to load the configuration using the ConfigLoader
    configs = ConfigLoader.load_compendium_config(config_path)
    print(configs)
    # Ensure that the returned object is a list of Compendium instances
    assert isinstance(configs, list)
    assert all(isinstance(config, Compendium) for config in configs)

    # Validate
