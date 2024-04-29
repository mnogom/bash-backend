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
from threading import Thread


class BashExecutor:
    def __init__(self):
        self.__pid: int | None = None
        self.__fd: int | None = None
        self.__poller: select.poll | None = None
        self.__max_read_bytes = 1024 * 60
        self.__poller_thread: Thread | None = None
        self.__process = None

    @property
    def fd(self) -> int:
        return self.__fd

    def create_tty(self, shell_command: str):
        self.__pid, self.__fd = pty.fork()
        if self.__pid == 0:
            self.__process = subprocess.call([shell_command])

    def change_tty_winsize(self, height: int, width: int):
        tty_wind_size = struct.pack("HHHH", height, width, 0, 0)
        fcntl.ioctl(self.__fd, termios.TIOCSWINSZ, tty_wind_size)

    def write_fd(self, command: bytes):
        os.write(self.__fd, command)

    def read_fd(self):
        select.select([self.__fd], [], [])
        return os.read(self.__fd, self.__max_read_bytes)

    def close(self):
        os.close(self.__fd)
        os.kill(self.__pid, signal.SIGKILL)
        os.waitpid(self.__pid, 0)  # omg. kill zombie process


class BashBuilder:
    def __init__(self, klass: type[BashExecutor]):
        self.__klass = klass

    def build(self, shell_command: str, height: int = 24, width: int = 80):
        instance = self.__klass()
        instance.create_tty(shell_command)
        instance.change_tty_winsize(height=height, width=width)
        return instance
