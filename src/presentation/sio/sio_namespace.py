import socketio
from loguru import logger

from src.infra.repos.bash_repo import BashInMemoryRepo
from src.service.bash.executor import BashBuilder, BashExecutor
from src.service.bash.poller import Poller

bash_builder = BashBuilder(BashExecutor)


class SioNamespace(socketio.AsyncNamespace):
    def __init__(
        self, *args, poller: Poller, bash_repo: BashInMemoryRepo, **kwargs
    ) -> None:
        self.__bash_repo = bash_repo
        self.__poller = poller
        super().__init__(*args, **kwargs)

    async def on_connect(self, sid, environ) -> None:
        logger.debug("connect %s" % sid)
        bash = bash_builder.build(
            shell_command="/bin/bash",
            height=24,
            width=80,
        )
        self.__poller.register_fd(bash.fd)
        self.__bash_repo.add(sid, bash)

    async def on_disconnect(self, sid) -> None:
        logger.debug("disconnect %s" % sid)
        bash = self.__bash_repo.pop(sid)
        bash.close()
        self.__poller.unregister_fd(bash.fd)

    async def on_message(self, sid, data) -> None:
        logger.debug("from %s receive message %s" % (sid, data[:100]))
        self.__bash_repo.get_bash_by_sid(sid).write_fd(data.encode() + b"\r")
