from abc import ABC, abstractmethod


class Service(ABC):

    @abstractmethod
    async def start(self):
        raise NotImplementedError()

    @abstractmethod
    async def stop(self):
        raise NotImplementedError()

    @abstractmethod
    async def shutdown(self):
        raise NotImplementedError()
