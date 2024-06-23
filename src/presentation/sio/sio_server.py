import socketio
from loguru import logger

from src.infra.repos.bash_repo import BashInMemoryRepo
from src.presentation.sio.sio_namespace import SioNamespace
from src.service.bash.executor import BashBuilder
from src.service.bash.poller import Poller


def get_sio_app(
    poller: Poller,
    bash_builder: BashBuilder,
    bash_repo: BashInMemoryRepo,
) -> socketio.ASGIApp:
    sio = socketio.AsyncServer(
        async_mode="asgi",
        cors_allowed_origins="*",
    )
    app = socketio.ASGIApp(sio)
    sio.register_namespace(
        SioNamespace(
            namespace="/",
            bash_builder=bash_builder,
            poller=poller,
            bash_repo=bash_repo,
        )
    )

    async def streaming() -> None:
        while True:
            message = await poller.queue.get()
            logger.debug(
                "Get message from queue for %s: %r"
                % (message.fd, message.output[:100])
            )
            sid = bash_repo.get_sid_by_fd(message.fd)
            data = message.output.decode()
            await sio.emit(
                event="pty",
                data=data,
                to=sid,
            )

    sio.start_background_task(streaming)
    return app
