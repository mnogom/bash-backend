import asyncio
import os
from logging import getLogger

from src.app import get_app
from src.config import Config

import uvicorn
from fastapi import FastAPI

logger = getLogger(__name__)


def get_server(app: FastAPI, config: Config):
    server = uvicorn.Server(
        config=uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=config.PORT,
        )
    )
    return server


async def run_server():
    config = Config()  # type: ignore[call-arg]
    app = get_app(config=config)
    server = get_server(app=app, config=config)
    await server.serve()


def main():
    try:
        asyncio.run(run_server())
    except (
        SystemExit,
        KeyboardInterrupt,
    ):
        exit(os.EX_OK)
    except Exception as error:
        logger.error(error)
        exit(os.EX_SOFTWARE)


if __name__ == "__main__":
    main()
