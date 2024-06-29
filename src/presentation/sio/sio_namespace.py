from urllib.parse import parse_qs

import socketio
from loguru import logger

from src.infra.repos.bash_repo import BashInMemoryRepo
from src.service.bash.executor import BashBuilder
from src.service.bash.poller import Poller


class SioNamespace(socketio.AsyncNamespace):
    def __init__(
        self,
        *args,
        bash_builder: BashBuilder,
        poller: Poller,
        bash_repo: BashInMemoryRepo,
        **kwargs
    ) -> None:
        self.__bash_repo = bash_repo
        self.__poller = poller
        self.__bash_builder = bash_builder
        super().__init__(*args, **kwargs)

    async def on_connect(self, sid: str, environ: dict) -> None:
        logger.debug("connection %s" % sid)
        query = environ["QUERY_STRING"]
        params = parse_qs(query)
        bash = self.__bash_builder.build(
            rows=int(params["rows"][0]),
            cols=int(params["cols"][0]),
        )
        self.__poller.register_fd(bash.fd)
        self.__bash_repo.add(sid, bash)

    async def on_disconnect(self, sid: str) -> None:
        logger.debug("disconnect %s" % sid)
        bash = self.__bash_repo.pop(sid)
        bash.close()
        self.__poller.unregister_fd(bash.fd)

    async def on_pty(self, sid: str, data: str) -> None:
        self.__bash_repo.get_bash_by_sid(sid).write_fd(data.encode())

    async def on_resize(self, sid: str, data: dict[str, str]) -> None:
        logger.debug("from %s receive resize message: %s" % (sid, data))
        self.__bash_repo.get_bash_by_sid(sid).change_tty_winsize(
            rows=int(data["rows"]), cols=int(data["cols"])
        )
