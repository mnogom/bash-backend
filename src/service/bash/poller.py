import asyncio
import os
import select
from threading import Thread

from src.dto import PollerMessage


class Poller:
    def __init__(self, queue: asyncio.Queue[PollerMessage]) -> None:
        self.__poller = select.poll()
        self.__max_read_bytes = 1024 * 60
        self.__timeout_ms = 1000
        self.__queue = queue

    @property
    def queue(self) -> asyncio.Queue[PollerMessage]:
        return self.__queue

    def register_fd(self, fd: int) -> None:
        self.__poller.register(fd, select.POLLIN)

    def unregister_fd(self, fd: int) -> None:
        self.__poller.unregister(fd)

    def __run_poller(self) -> None:
        while True:
            events = self.__poller.poll(self.__timeout_ms)
            for fd, event in events:
                if event is select.POLLIN:
                    output = PollerMessage(
                        fd=fd,
                        output=os.read(fd, self.__max_read_bytes),
                    )
                    self.queue.put_nowait(output)

    def start(self) -> None:
        Thread(target=self.__run_poller, daemon=True).start()
