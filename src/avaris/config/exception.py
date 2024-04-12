import asyncio
from avaris.config.error import ConfigError, ConnectionError


class ExceptionHandler:

    def __init__(self, logger, loop=None):
        self.logger = logger
        self.loop = loop

    def handle_exception(self, error):
        if isinstance(error, ConfigError):
            self.logger.critical(f"Configuration error: {error}")
            # Specific handling for configuration errors
        elif isinstance(error, ConnectionError):
            self.logger.error(f"Network connection error: {error}")
            # Handling for network errors
        else:
            self.logger.error(f"Unexpected error: {error}")
            # General error handling

        if self.loop:
            self.shutdown_loop()

    def shutdown_loop(self):
        if self.loop.is_running():
            for task in asyncio.all_tasks(self.loop):
                task.cancel()
            self.loop.stop()
            self.logger.info("Shutdown complete.")
