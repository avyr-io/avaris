# test_compendium.py

import pytest
from pathlib import Path
from avaris.config.config_loader import ConfigLoader
from avaris.config.error import ConfigError


@pytest.fixture
def valid_config_path(tmp_path) -> Path:
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
          task: http_get_request
          parameters:
            url: 'https://example.com'
    """
    path = tmp_path / "valid_compendium.yml"
    path.write_text(config_content)
    return path


@pytest.fixture
def invalid_config_path(tmp_path) -> Path:
    config_content = """
invalid_compendium:
  - name: ExampleCompendium
    """
    path = tmp_path / "invalid_compendium.yml"
    path.write_text(config_content)
    return path


def test_load_valid_compendium_config(valid_config_path):
    compendiums = ConfigLoader.load_compendium_config(valid_config_path)
    assert isinstance(compendiums, list)
    assert len(compendiums) > 0
    assert compendiums[0].name == "ExampleCompendium"


def test_load_invalid_compendium_config(invalid_config_path):
    with pytest.raises(ConfigError):
        ConfigLoader.load_compendium_config(invalid_config_path)
