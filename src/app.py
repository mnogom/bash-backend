import asyncio

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config import Config
from src.infra.repos.bash_repo import BashInMemoryRepo
from src.presentation.sio.sio_server import get_sio_app
from src.presentation.api.router import service_router
from src.service.bash.executor import BashBuilder, BashExecutor
from src.service.bash.poller import Poller


def get_app(config: Config) -> FastAPI:
    app = FastAPI(
        title=config.APP_NAME,
        debug=config.DEBUG,
        docs_url=None,
        redoc_url=None
    )
    # CORS policy
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Register routes
    app.include_router(
        router=service_router,
        prefix="/service",
        tags=["internal"]
    )
    # Run poller
    poller = Poller(asyncio.Queue())
    poller.start()

    # Create bash repo
    bash_repo = BashInMemoryRepo()

    # Create bash builder
    bash_builder = BashBuilder(
        klass=BashExecutor,
        shell_command=config.SHELL_COMMAND,
    )

    # Get soket.io app
    sio_app = get_sio_app(
        poller=poller,
        bash_repo=bash_repo,
        bash_builder=bash_builder,
    )
    app.mount(path="/socket.io/", app=sio_app)
    return app
