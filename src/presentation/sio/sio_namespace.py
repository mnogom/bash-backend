import socketio
from loguru import logger

from src.service.bash.executor import BashBuilder, BashExecutor
from src.service.bash.poller import Poller

bash_builder = BashBuilder(BashExecutor)


class SioNamespace(socketio.AsyncNamespace):
    def __init__(
        self, *args, poller: Poller, bash_repo: dict[str, BashExecutor], **kwargs
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
        self.__bash_repo[sid] = bash

    async def on_disconnect(self, sid) -> None:
        logger.debug("disconnect %s" % sid)
        bash = self.__bash_repo.pop(sid)
        bash.close()
        self.__poller.unregister_fd(bash.fd)

    async def on_message(self, sid, data) -> None:
        logger.debug("message %s %s" % (sid, data[:100]))
        self.__bash_repo[sid].write_fd(data.encode() + b"\r")
