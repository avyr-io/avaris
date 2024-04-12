import os
import signal
from pathlib import Path

import click
from avaris.defaults import Defaults

from avaris.config.config_manager import ConfigManager
from avaris.engine.start import start_engine

manager = ConfigManager()
engine_pid_file = Path("engine.pid")  # Adjust as needed

@click.group()
def avaris():
    """Avaris Task Engine CLI."""
    pass


@click.argument('path', type=click.Path(), required=False)
@avaris.command()
def init(path):
    """Initialize a new Avaris project and virtual environment."""
    project_dir = Path(path) if path else Path.cwd(
    )
    compendium_dir = project_dir / "compendium"
    compendium_dir.mkdir(parents=True, exist_ok=True)
    #os.environ["WORKINGDIR"] = project_dir.as_posix()
    #os.environ["COMPENDIUM"] = compendium_dir.as_posix()
    executor_dir = project_dir / ".avaris" / "src" / "plugins" / "executor"
    executor_dir.mkdir(parents=True, exist_ok=True)
    Path.cwd()
    (executor_dir / "__init__.py").touch()
    (executor_dir.parent / "__init__.py").touch()  # For 'plugins' directory
    (executor_dir.parent.parent / "__init__.py").touch()  # For 'src' directory

    click.echo(f"Initialized Avaris project in {project_dir}")

@click.option(
    "-c",
    "--config",
    "config_file",
    default=(
        Defaults.DEFAULT_CONF_FILE.as_posix() if Defaults.DEFAULT_CONF_FILE else None
    ),
    required=False,
    help="Path to the engine configuration YAML file.",
    type=click.Path(),
)
@click.option(
    "-d",
    "--compendium-dir",
    "compendium_directory",
    required=False,  # No longer strictly required
    default=None,
    help="Path to the directory containing compendium configurations.",
    type=click.Path(),
)
@click.option(
    "-f",
    "--compendium-file",
    "compendium_file",
    required=False,
    default=None,
    help="Path to a single compendium configuration file.",
    type=click.Path(),
)
@click.option(
    "-p",
    "--plugins-dir",
    "plugins_directory",
    required=False,
    default=(Defaults.DEFAULT_PLUGINS_DIR if Defaults.DEFAULT_PLUGINS_DIR else None),
    help="Path to the directory containing plugin modules. Defaults to $PWD/.avaris/plugins",
    type=click.Path(),
)
@avaris.command()
def start(config_file, compendium_directory, compendium_file, plugins_directory):
    """
    Start the engine with the specified configuration.
    You must specify either a compendium directory or a compendium file.
    Optionally, you can specify a plugins directory.
    """
    if not compendium_directory and not compendium_file:
        raise click.UsageError(
            "You must specify either a compendium directory or a compendium file."
        )

    start_engine(config_file, compendium_directory, compendium_file, plugins_directory)


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

def entrypoint(args):
    avaris(args)
