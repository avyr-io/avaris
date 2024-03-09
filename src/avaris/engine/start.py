import asyncio
import importlib
import os
import signal
import sys
from pathlib import Path
from avaris.service.service import Service
import avaris.registry as registry
from avaris.data.datamanager import DataManager
from avaris.config.config_loader import ConfigLoader
from avaris.config.error import ConfigError
from avaris.api.models import AppConfig
from avaris.data.s3 import S3DataManager
from avaris.data.sql import SQLDataManager
from avaris.engine.engine import AvarisEngine
from avaris.handler.handler import ResultHandler
from avaris.service.datasource import DataSourceService
from avaris.task.taskmaster_apscheduler import APSchedulerTaskMaster
from avaris.utils.logging import get_logger
from typing import List
from avaris.engine.commands import AvarisEngineCommands
from dotenv import load_dotenv
from avaris.defaults import Defaults,Names
logger = get_logger()


async def command_dispatcher(engine: AvarisEngine,
                             command_queue: asyncio.Queue):
    while True:
        command = await command_queue.get()
        if command == AvarisEngineCommands.START:
            await engine.start()
        elif command == AvarisEngineCommands.STOP:
            engine.stop()
        elif command == AvarisEngineCommands.SHUTDOWN:
            await engine.shutdown()
            break
        elif command == AvarisEngineCommands.RELOAD:
            engine.stop()
            await engine.start()
        command_queue.task_done()


async def shutdown_procedures(engine: AvarisEngine,
                              services: List[Service] = None):
    logger.info("Initiating shutdown procedures...")
    await engine.shutdown()
    if services:
        for service in services:
            await service.shutdown()  # Assuming this is now an async method
    # Cancel all remaining asyncio tasks
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("Shutdown procedures completed.")


def setup_signal_handlers(loop: asyncio.AbstractEventLoop,
                          command_queue: asyncio.Queue):

    async def handle_signal():
        await command_queue.put(AvarisEngineCommands.SHUTDOWN)

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig,
                                lambda: asyncio.create_task(handle_signal()))


async def main(avaris_config_path: str, scraper_config_dir: str):
    config = ConfigLoader.load_global_config(avaris_config_path)
    services: List[Service] = []
    loop = asyncio.get_running_loop()
    command_queue = asyncio.Queue()
    asyncio.get_event_loop().set_debug(True)
    # Data Backend Setup
    data_manager = await setup_data_manager(config)

    #Services Setup
    if config.services["datasource"].enabled:
        datasource_service = setup_datasource_service(config, data_manager)
        services.append(datasource_service)

    # Avaris Engine Setup
    engine, dispatcher_task = setup_avaris_engine(scraper_config_dir,
                                                  data_manager, command_queue)

    # Register signal handlers for graceful shutdown
    setup_signal_handlers(loop, command_queue)
    await engine.start()
    await dispatcher_task  # Ensures that the dispatcher task runs and can be cleanly shut down


async def setup_data_manager(config: AppConfig):
    if config.data_backend.backend == Names.SQLITE:
        database_url = config.data_backend.database_url or Defaults.DEFAULT_SQLITE_PATH
        data_manager = SQLDataManager(logger=logger, database_url=database_url)
    elif config.data_backend == Names.S3:
        data_manager = S3DataManager(logger=logger)
    else:
        raise ConfigError(f"Unknown data backend: {config.data_backend}")
    await data_manager.init_db()
    return data_manager


def setup_datasource_service(config:AppConfig, data_manager: DataManager):
    datasource_port = config.services["datasource"].port
    datasource_service = DataSourceService(data_manager=data_manager,
                                     port=datasource_port,logger=logger)
    asyncio.create_task(datasource_service.start())
    return datasource_service


def setup_avaris_engine(scraper_config_dir, data_manager, command_queue):
    result_handler = ResultHandler(data_manager=data_manager, logger=logger)
    task_master = APSchedulerTaskMaster(logger=logger,
                                        task_registry=registry.task_registry,
                                        result_handler=result_handler,
                                        use_daemon=True)
    engine = AvarisEngine(data_manager=data_manager,
                          task_master=task_master,
                          scraper_config_dir=Path(scraper_config_dir),
                          logger=logger)
    dispatcher_task = asyncio.create_task(
        command_dispatcher(engine, command_queue))
    return engine, dispatcher_task


def import_package_modules():
    import pkgutil
    import avaris.executor as executor_package

    for _, modname, ispkg in pkgutil.iter_modules(executor_package.__path__):
        full_module_name = f"{executor_package.__name__}.{modname}"
        if not ispkg:
            __import__(full_module_name)


def import_plugin_modules(plugins_dir: Path):
    if  plugins_dir not in sys.path:
        sys.path.append(str(plugins_dir))
    for path in plugins_dir.glob("**/*.py"):
        if path.name == "__init__.py":
            continue
        module_path = f"plugins.executor.{path.stem}"
        try:
         
            importlib.import_module(module_path)
            logger.info(f"Successfully imported {module_path}")
        except ModuleNotFoundError as e:
            logger.error(f"Failed to import {module_path}: {e}")




def start_engine(avaris_config_file:str, scraper_config_directory:str, plugins_directory:str=None):
    import_package_modules()
    avaris_config_file = Path(avaris_config_file) if Path(avaris_config_file).exists() else None
    plugins_dir = Path(plugins_directory if plugins_directory else Path.cwd() / ".avaris"/"src")
    if plugins_dir: 
        logger.info(f"Using plugins directory: {plugins_dir}")
    if plugins_dir.exists():
        import_plugin_modules(plugins_dir)
    asyncio.run(main(avaris_config_file, scraper_config_directory))


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "Usage: python -m engine.start --config <config_file> --scraper-dir <scraper_directory>"
        )
        sys.exit(1)

    if sys.argv[1] == "start":
        base_dir = Path(__file__).resolve().parent.parent.parent
        config_file_index = sys.argv.index("--config") + 1
        scraper_dir_index = sys.argv.index("--scraper-dir") + 1
        avaris_config_path = sys.argv[config_file_index]
        scraper_config_dir = sys.argv[scraper_dir_index]


        start_engine(avaris_config_path, scraper_config_dir)
