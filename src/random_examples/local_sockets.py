import socket
from types import TracebackType
from typing import BinaryIO, Self


class LocalEmitter:
    def __init__(self, address: tuple[str, int]) -> None:
        self.address = address
        self._sock: socket.socket | None = None
        self._responses: BinaryIO | None = None

    def __enter__(self) -> Self:
        self._sock = socket.create_connection(self.address)
        self._responses = self._sock.makefile("rb")
        return self

    def emit(self, message: str) -> None:
        if self._sock is None or self._responses is None:
            error_message = "LocalEmitter must be used inside a with block"
            raise RuntimeError(error_message)
        if "\n" in message or "\r" in message:
            error_message = "Messages cannot contain newline characters"
            raise ValueError(error_message)

        self._sock.sendall(message.encode("utf-8") + b"\n")
        response = self._responses.readline()
        if response == b"":
            error_message = "Receiver closed before acknowledging the job"
            raise ConnectionError(error_message)

        decoded = response.decode("utf-8", errors="replace")
        if decoded != "OK\n":
            error_message = f"Receiver returned an unexpected response: {response!r}"
            raise RuntimeError(error_message)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._responses is not None:
            self._responses.close()
            self._responses = None
        if self._sock is not None:
            self._sock.close()
            self._sock = None
