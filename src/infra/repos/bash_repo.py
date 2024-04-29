from src.service.bash.executor import BashExecutor


class BashInMemoryRepo:
    def __init__(self) -> None:
        self.__repo: dict[str, BashExecutor] = {}

    def add(self, sid: str, bash: BashExecutor) -> None:
        self.__repo[sid] = bash

    def pop(self, sid: str) -> BashExecutor:
        return self.__repo.pop(sid)

    def get_bash_by_sid(self, sid: str) -> BashExecutor:
        return self.__repo[sid]

    def get_sid_by_fd(self, fd: int) -> str:
        return next(sid for sid, bash in self.__repo.items() if bash.fd == fd)
