import argparse
import logging
import socketserver
from collections.abc import Iterable, Iterator

LOGGER = logging.getLogger(__name__)


def iter_messages(stream: Iterable[bytes]) -> Iterator[str]:
    for line in stream:
        message = line.decode("utf-8").removesuffix("\n").removesuffix("\r")
        yield message


def consume_message(message: str) -> None:
    LOGGER.info("Received: %s", message)


class LineMessageHandler(socketserver.StreamRequestHandler):
    """
    self.rfile is a buffered, read-only stream of bytes that socketserver.StreamRequestHandler
    creates for the current client connection.

    In this handler, for message in iter_messages(self.rfile) reads from that stream line by line.
    Each line ends when the client sends a newline (\n); the listener then decodes it as UTF-8.
    The matching self.wfile is the stream for sending data back to the client.
    """
    def handle(self) -> None:
        for message in iter_messages(self.rfile):
            consume_message(message)


class ThreadedTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def serve(host: str = "127.0.0.1", port: int = 9000) -> None:
    with ThreadedTCPServer((host, port), LineMessageHandler) as server:
        LOGGER.info("Listening on %s:%s", host, port)
        server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Listen for newline-delimited TCP messages."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=9000, type=int)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    serve(args.host, args.port)


if __name__ == "__main__":
    main()
