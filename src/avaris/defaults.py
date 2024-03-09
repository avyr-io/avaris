from pathlib import Path
import os
class Names:
    SCRAPER_IDENTIFIER = "scraper"
    SQLITE="sqlite"
    S3="s3"
class Defaults:
    # Attempt to determine the correct configuration file path
    DEFAULT_CONF_PATH = Path.home() / ".avaris" / "conf.yaml" if (Path.home() / ".avaris" / "conf.yaml").exists() else Path("/") / "etc"/ "avaris" / "conf.yaml"
    DEFAULT_SQLITE_PATH = f"sqlite+aiosqlite:///{(Path(os.getenv('DATA') or Path.cwd()).absolute() / 'local.db').resolve()}"
    
    @classmethod
    def print_all(cls):
        for attr, value in cls.__dict__.items():
            if not attr.startswith("__") and not callable(value):
                print(f"{attr}: {value}")

    DEFAULT_CONF = """
    execution_backend: apscheduler
    data_backend:
      backend: sqlite
      database_url: 
    services:
      datasource:
        enabled: true
        port: 5000
    """

if __name__ == "__main__":
    Defaults.print_all()
