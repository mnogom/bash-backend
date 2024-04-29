import asyncio

import socketio

from src.service.bash.executor import BashBuilder, BashExecutor
from src.service.bash.poller import Poller

bash_builder = BashBuilder(BashExecutor)


class SioNamespace(socketio.AsyncNamespace):
    def __init__(
        self,
        *args,
        poller: Poller,
        bash_repo: dict[str, BashExecutor],
        **kwargs
    ) -> None:
        self.__bash_repo = bash_repo
        self.__poller = poller
        super().__init__(*args, **kwargs)

    async def on_connect(self, sid, environ) -> None:
        # ========================================
        # print("connect ", sid)
        # self.__clients_repo.add_client(sid)
        # ========================================
        bash = bash_builder.build(
            shell_command="/bin/bash",
            height=24,
            width=80,
        )
        self.__poller.register_fd(bash.fd)
        self.__bash_repo[sid] = bash

    async def on_disconnect(self, sid) -> None:
        # ========================================
        # print("disconnect ", sid)
        # self.__clients_repo.remove_client(sid)
        # ========================================
        bash = self.__bash_repo.pop(sid)
        bash.close()
        self.__poller.unregister_fd(bash.fd)

    async def on_message(self, sid, data) -> None:
        print("message ", sid, data)
        # ========================================
        # queue = self.__clients_repo.get_client(sid)
        # await queue.put(data)
        # message = await queue.get()
        # await self.emit("message", message, to=sid)
        # ========================================

        self.__bash_repo[sid].write_fd(data.encode() + b"\r")
