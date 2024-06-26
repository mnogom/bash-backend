# Examples:
#   https://jvns.ca/blog/2022/07/20/pseudoterminals/
#   https://github.com/cs01/pyxtermjs
import fcntl
import os
import pty
import select
import signal
import struct
import subprocess
import termios

from loguru import logger


class BashExecutor:
    def __init__(self) -> None:
        self.__pid: int | None = None
        self.__fd: int | None = None
        self.__max_read_bytes = 1024 * 60

    @property
    def fd(self) -> int:
        return self.__fd

    @property
    def pid(self) -> int:
        return self.__pid

    def create_tty(self, command: list[str]) -> None:
        self.__pid, self.__fd = pty.fork()
        if self.pid == 0:
            subprocess.call(command, shell=False)
        logger.info("Create tty pid/fd: %s/%s" % (self.pid, self.fd))

    def change_tty_winsize(self, rows: int, cols: int) -> None:
        logger.info(
            "Change tty size to: %s x %s for pid/fd: %s/%s"
            % (rows, cols, self.pid, self.fd)
        )
        tty_wind_size = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, tty_wind_size)

    def write_fd(self, command: bytes) -> None:
        os.write(self.fd, command)

    def read_fd(self) -> bytes:
        select.select([self.fd], [], [])
        return os.read(self.fd, self.__max_read_bytes)

    def close(self) -> None:
        logger.info("Close pid/fd: %s/%s" % (self.pid, self.fd))
        os.close(self.fd)
        os.kill(self.pid, signal.SIGKILL)
        os.waitpid(self.pid, 0)  # omg. kill zombie process


class BashBuilder:
    def __init__(self, klass: type[BashExecutor], shell_command: str) -> None:
        self.__klass = klass
        self.__shell_command = shell_command.split(" ")
        logger.debug("Create bash with command: %s" % self.__shell_command)

    def build(self, rows: int, cols: int) -> BashExecutor:
        instance = self.__klass()
        instance.create_tty(self.__shell_command)
        instance.change_tty_winsize(rows=rows, cols=cols)
        return instance
