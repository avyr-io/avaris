class ConfigError(Exception):
    """Base class for configuration-related exceptions."""

    pass


class NotCompendiumFileError(ConfigError):
    """Exception raised when the 'compendium' key is missing in the configuration."""

    def __init__(self, message="No 'compendium' key found in YAML."):
        self.message = message
        super().__init__(self.message)

class TaskExecutionError(Exception):
    """Exception raised when task execution goes wrong."""
