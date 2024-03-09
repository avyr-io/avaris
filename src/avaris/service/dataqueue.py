import asyncio

class DataQueueService:

    def __init__(self, data_queue: asyncio.Queue):
        self.data_queue = data_queue

    async def run(self):
        while True:
            # Example: fetch or generate data to be consumed by datasourceDataSourceHandler
            data = {"key": "service_data", "value": "example"}
            await self.data_queue.put(data)
            await asyncio.sleep(10) 
