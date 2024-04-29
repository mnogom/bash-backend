from time import sleep

import socketio

from src.presentation.sio.sio_namespace import SioNamespace
from src.service.bash.executor import BashExecutor
from src.service.bash.poller import Poller

bash_repo: dict[str, BashExecutor] = {}

def get_sio_app(
    poller: Poller,
):
    sio = socketio.AsyncServer(async_mode="asgi")
    app = socketio.ASGIApp(sio)
    sio.register_namespace(
        SioNamespace(
            namespace="/",
            poller=poller,
            bash_repo=bash_repo,
        )
    )

    async def streaming(*args, **kwargs):
        while True:
            msg = await poller.queue.get()
            print(f"--> from queue: {msg=}")
            fd = msg.fd
            output = msg.output
            sid = next(sid for sid in bash_repo if bash_repo[sid].fd == fd)
            await sio.emit("message", output.decode(), to=sid)

    sio.start_background_task(streaming)
    return app
