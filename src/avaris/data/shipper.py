from avaris.handler.handler import ResultHandler


class DatabaseShipperHandler(ResultHandler):

    async def handle_result(self, task_result: dict, **kwargs):
        raise NotImplementedError()
