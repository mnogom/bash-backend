from pydantic_settings import BaseSettings


class Config(BaseSettings):
    APP_NAME: str
    HOST: str
    PORT: int
    DEBUG: bool
    SHELL_COMMAND: str
