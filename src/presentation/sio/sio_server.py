import socketio
from loguru import logger

from src.presentation.sio.sio_namespace import SioNamespace
from src.service.bash.executor import BashExecutor
from src.service.bash.poller import Poller


def get_sio_app(
    poller: Poller,
    bash_repo: dict[str, BashExecutor],
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

    async def streaming():
        while True:
            message = await poller.queue.get()
            logger.debug(f"Get message from queue for: {message.fd=}")
            sid = next(sid for sid in bash_repo if bash_repo[sid].fd == message.fd)
            await sio.emit(
                event="message",
                data=message.output.decode(),
                to=sid,
            )

    sio.start_background_task(streaming)
    return app
