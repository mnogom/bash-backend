from dataclasses import dataclass


@dataclass(slots=True)
class PollerMessage:
    fd: int
    output: bytes
