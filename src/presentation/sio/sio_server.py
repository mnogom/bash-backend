import socketio

from src.presentation.sio.sio_namespace import SioNamespace
from src.protocols.repos import ClientsRepoProtocol
from src.service.bash.poller import Poller


def get_sio_app(
    clients_repo: ClientsRepoProtocol,
    poller: Poller,
):
    sio = socketio.AsyncServer(async_mode="asgi")
    app = socketio.ASGIApp(sio)
    sio.register_namespace(
        SioNamespace(
            namespace="/",
            clients_repo=clients_repo,
            poller=poller,
        )
    )
    return app
