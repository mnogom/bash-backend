import socketio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config import Config
from src.infra.repos.clients import ClientsRepo
from src.presentation.sio.sio_server import get_sio_app
from src.service.bash.poller import Poller


def get_app(config=Config):
    app = FastAPI(title=config.APP_NAME, debug=config.DEBUG)
    # TODO: check if need it
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Init clients repo
    clients_repo = ClientsRepo()

    # Run poller
    poller = Poller()
    poller.start()

    app.state.config = config
    sio_app = get_sio_app(clients_repo=clients_repo, poller=poller)
    app.mount("/socket.io/", sio_app)
    return app
