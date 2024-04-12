from typing import Optional
from avaris.data.datamanager import DataManager
from logging import Logger


class S3DataManager(DataManager):

    def __init__(self, s3_client_config:dict, logger: Optional[Logger] = None):
        super().__init__(logger)

    async def init_db(self):
        raise NotImplementedError("Not implemented : )")

