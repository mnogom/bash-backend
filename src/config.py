from pydantic import BaseConfig


class Config(BaseConfig):
    APP_NAME: str = "Freidlin BASH"
    PORT: int = 8080
    DEBUG: bool = True

    SHELL: str = "/bin/bash"
