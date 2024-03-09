import os
import signal
from pathlib import Path
import click
from avaris.config.config_manager import ConfigManager
from avaris.engine.start import start_engine
from avaris.defaults import Defaults
manager = ConfigManager()
engine_pid_file = Path("engine.pid")  # Adjust as needed

@click.group()
def avaris():
    """Avaris Task Engine CLI."""
    pass

@avaris.command()
def init():
    """Initialize a new Avaris project and virtual environment."""
    project_dir = Path.cwd() / ".avaris"
    project_dir.mkdir(exist_ok=True)
    # Add logic to create virtual environment and project structure
    # Spin up the virtual environment
    click.echo(f"Initialized Avaris project in {Path.cwd()}")

@click.option(
    "-c",
    "--config",
    "config_file",
    default=lambda: Defaults.DEFAULT_CONF_PATH.as_posix(),
    required=True,
    help="Path to the engine configuration YAML file.",
    type=click.Path(),
)
@click.option(
    "-s",
    "--scraper-dir",
    "scraper_directory",
    required=True,
    help="Path to the directory containing scraper configurations.",
)
@avaris.command()
def start(config_file, scraper_directory):
    """Start the engine with the specified configuration."""
    start_engine(config_file, scraper_directory)


@avaris.command(name="ls")
def list_instances():
    """List all engine instances."""
    instances_dir = Path.home() / "avaris" / "instances"
    for instance_dir in instances_dir.iterdir():
        if instance_dir.is_dir():
            click.echo(f"Instance ID: {instance_dir.name}")


@avaris.command(name="stop")
def stop():
    """Stop the engine."""
    if engine_pid_file.exists():
        pid = int(engine_pid_file.read_text())
        os.kill(pid, signal.SIGTERM)
        engine_pid_file.unlink()
        click.echo("AvarisEngine stopped.")
    else:
        click.echo("AvarisEngine is not running.")
