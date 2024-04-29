import asyncio
from logging import getLogger

from src.protocols.repos import ClientsRepoProtocol

logger = getLogger(__name__)


class ClientsRepo(ClientsRepoProtocol):
    __clients: dict[str, asyncio.Queue] = {}

    def __len__(self) -> int:
        return len(self.__clients)

    def has_client(self, sid: str) -> bool:
        print("client exists: %s" % (sid in self.__clients))
        return sid in self.__clients

    def add_client(self, sid: str) -> None:
        self.__clients[sid] = asyncio.Queue()
        print("create queue for client: %s, total: %s" % (sid, len(self)))

    def get_client(self, sid: str) -> asyncio.Queue:
        print("get queue for client: %s", sid)
        return self.__clients[sid]

    def remove_client(self, sid: str) -> None:
        self.__clients.pop(sid)
        print("remove queue for client: %s, total: %s" % (sid, len(self)))
