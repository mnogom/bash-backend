import os
import select
from threading import Thread


class Poller:
    def __init__(self):
        self.__poller = select.poll()
        self.__max_read_bytes = 1024 * 60
        self.__timeout_ms = 1000

    def register_fd(self, fd: int) -> None:
        self.__poller.register(fd, select.POLLIN)

    def unregister_fd(self, fd: int) -> None:
        self.__poller.unregister(fd)

    def __run_poller(self):
        while True:
            events = self.__poller.poll(self.__timeout_ms)
            for fd, event in events:
                if event is select.POLLIN:
                    output = os.read(fd, self.__max_read_bytes)
                    print(f"===\n{fd=}\n{event=}\n{output=}\n===")

    def start(self):
        Thread(target=self.__run_poller, daemon=True).start()
