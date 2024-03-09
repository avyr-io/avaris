class ConfigError(Exception):
    """Base class for configuration-related exceptions."""
    pass


class MissingScraperKeyError(ConfigError):
    """Exception raised when the 'scraper' key is missing in the configuration."""

    def __init__(self, message="No 'scraper' key found in YAML."):
        self.message = message
        super().__init__(self.message)
