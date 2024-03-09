from datetime import datetime
from logging import Logger
from avaris.service.service import Service
from fastapi import FastAPI, Request
from uvicorn import Config, Server
from avaris.data.datamanager import DataManager
from avaris.utils.logging import get_logger
import multiprocessing
from typing import List
from avaris.api.models import ExecutionResult


class UvicornServer(multiprocessing.Process):

    def __init__(self, config: Config):
        super().__init__()

        self.config = config

    def stop(self):
        self.terminate()

    def run(self, *args, **kwargs):
        server = Server(config=self.config)
        server.run()


class DataSourceService(Service):

    def __init__(self,
                 data_manager: DataManager,
                 port: int = 5000,
                 logger: Logger = None):
        self.data_manager = data_manager
        self.port = port
        self.logger = logger or get_logger()
        self.app = FastAPI(title="datasource Data Source Service")
        self.setup_routes()

        self.config = Config(app=self.app,
                             host="0.0.0.0",
                             port=self.port,
                             log_level="info",
                             loop="asyncio")
        self.server = UvicornServer(config=self.config)

    def setup_routes(self):

        @self.app.post("/metrics")
        async def post_metrics():
            metrics = await self.data_manager.get_all_task_names()
            return metrics

        @self.app.post("/search")
        async def search():
            # Fetch a list of unique task names or identifiers from the database
            tasks: List[str] = await self.data_manager.get_all_task_names()
            return tasks


        @self.app.post("/query")
        async def query(request: Request):
            try:
                req_body = await request.json()
                from_time_str, to_time_str = (
                    req_body["range"]["from"],
                    req_body["range"]["to"],
                )
                from_time = datetime.strptime(from_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                to_time = datetime.strptime(to_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")

                # Fetch task results within the specified time range.
                task_results: List[
                    ExecutionResult] = await self.data_manager.get_slice(
                        from_time, to_time)

                datasource_response = []

                for task_result in task_results:
                    task_time = task_result.timestamp.timestamp(
                    ) * 1000  # Convert to milliseconds for datasource

                    # Ensure 'result' is in the expected format or adapt as necessary
                    for metric_name, metric_value in task_result.result.items():
                        # Find or create the series for this metric
                        series = next((item for item in datasource_response
                                    if item["target"] == metric_name), None)
                        if not series:
                            series = {"target": metric_name, "datapoints": []}
                            datasource_response.append(series)

                        # Add the datapoint for this metric
                        series["datapoints"].append([metric_value, task_time])

                return datasource_response
            except Exception as e:
                self.logger.error(f"Error querying Data Source: {e}")
                return {"error": f"Error querying Data Source: {e}"}

        @self.app.post("/annotations")
        async def annotations():
            # Implement if you need annotations feature
            # This should return a list of annotations.
            return []

        @self.app.get("/health")
        async def health_check():
            return {"status": "ok"}

        @self.app.get("/tasks")
        async def get_all_tasks():
            tasks = await self.data_manager.get_all_tasks()
            return tasks

    async def start(self) -> bool:
        # Runs Uvicorn server in the same asyncio event loop
        try:
            self.server.start()
            return True
        except Exception as e:
            self.logger.error(f"Error starting datasource Service: {e}")
            return False

    async def stop(self) -> bool:
        try:
            self.server.stop()
            self.logger.info("datasource Service stopped.")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping datasource Service: {e}")
            return False

    async def shutdown(self) -> bool:
        try:
            self.stop()
            return True
        except Exception as e:
            self.logger.error(f"Error shutting down datasource Service: {e}")
            return False
