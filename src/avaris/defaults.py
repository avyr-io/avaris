import os
from pathlib import Path

from avaris.utils.parse import (
    ensure_directory,
    find_first_existing_directory,
    find_first_existing_file,
)


class Names:
    COMPENDIUM_IDENTIFIER = "compendium"
    SQLITE = "sqlite"
    S3 = "s3"
    LISTENER_TASK= "listener_task"

class Defaults:
    CWD=Path.cwd()
    DEFAULT_HOME_DIR = Path.home().absolute() / ".avaris"
    # Attempt to determine the correct configuration file path
    DEFAULT_WORKINGDIR = (
        Path(os.getenv("WORKINGDIR")) or DEFAULT_HOME_DIR or CWD)

    DEFAULT_WORKINGDIR.mkdir(parents=True, exist_ok=True)
    # For directories, we ensure they exist or create them if they don't
    DEFAULT_DATA_DIR = ensure_directory(
        os.getenv("DATA") if os.getenv("DATA") else DEFAULT_WORKINGDIR / "data"
    )

    # Find the configuration file; ensure_directory is not applied here since it's a file search
    DEFAULT_CONF_FILE = find_first_existing_file(
        os.getenv("CONFIG"),
        CWD / "conf.yaml",
        DEFAULT_HOME_DIR / "conf.yaml",
        Path("/") / "etc" / "avaris" / "conf.yaml",
    ) or None # then just fail.
    DEFAULT_SQLITE_PATH = f"sqlite+aiosqlite:///{DEFAULT_DATA_DIR / 'local.db'}"

    DEFAULT_PLUGINS_DIR = (
        find_first_existing_directory(
            DEFAULT_WORKINGDIR / ".avaris",
            DEFAULT_HOME_DIR / ".avaris",
        )
        or DEFAULT_WORKINGDIR / ".avaris"
    )
    DEFAULT_LOG_FILE = find_first_existing_file(
        os.getenv("LOGS"), CWD / "avaris.log", DEFAULT_HOME_DIR / "avaris.log",
        Path("/") / "var" / "lib" / "etc" / "avaris" /
        "avaris.log") or CWD / "avaris.log"
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
    DEFAULT_COMPENDIUM_DIR = (
        find_first_existing_directory(
            Path(os.environ.get("COMPENDIUM","")), DEFAULT_WORKINGDIR / "compendium"
        )
        or DEFAULT_WORKINGDIR / "compendium"
    )
    DEFAULT_COMPENDIUM_DIR.mkdir(parents=True, exist_ok=True)


class Secrets:
    LISTENER_KEY = os.getenv("LISTENER_KEY") or None


if __name__ == "__main__":
    Defaults.print_all()
