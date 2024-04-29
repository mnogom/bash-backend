import socketio
from loguru import logger

from src.infra.repos.bash_repo import BashInMemoryRepo
from src.presentation.sio.sio_namespace import SioNamespace
from src.service.bash.poller import Poller


def get_sio_app(
    poller: Poller,
    bash_repo: BashInMemoryRepo,
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
            sid = bash_repo.get_sid_by_fd(message.fd)
            await sio.emit(
                event="message",
                data=message.output.decode(),
                to=sid,
            )

    sio.start_background_task(streaming)
    return app
