# ruff: noqa: PT009, PT027

import shutil
import socket
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from random_examples.local_sockets import LocalEmitter


class LocalEmitterTests(unittest.TestCase):
    def test_sends_newline_delimited_utf8_messages(self):
        received = []
        messages_received = threading.Event()

        def receive_messages(server: socket.socket) -> None:
            connection, _ = server.accept()
            with connection, connection.makefile("r", encoding="utf-8") as stream:
                for line in stream:
                    received.append(line.rstrip("\n"))
                    connection.sendall(b"OK\n")
                messages_received.set()

        with socket.socket() as server:
            server.bind(("127.0.0.1", 0))
            server.listen()
            thread = threading.Thread(
                target=receive_messages, args=(server,), daemon=True
            )
            thread.start()

            with LocalEmitter(("127.0.0.1", server.getsockname()[1])) as emitter:
                emitter.emit("hello")
                emitter.emit("caf\u00e9")

            self.assertTrue(messages_received.wait(timeout=2))
            self.assertEqual(received, ["hello", "caf\u00e9"])

    def test_raises_if_receiver_closes_without_acknowledging(self):
        def close_connection(server: socket.socket) -> None:
            connection, _ = server.accept()
            with connection:
                connection.recv(1024)

        with socket.socket() as server:
            server.bind(("127.0.0.1", 0))
            server.listen()
            thread = threading.Thread(
                target=close_connection, args=(server,), daemon=True
            )
            thread.start()

            with (
                LocalEmitter(("127.0.0.1", server.getsockname()[1])) as emitter,
                self.assertRaisesRegex(ConnectionError, "before acknowledging"),
            ):
                emitter.emit("job")

    def test_requires_context_manager(self):
        emitter = LocalEmitter(("127.0.0.1", 8080))

        with self.assertRaisesRegex(RuntimeError, "with block"):
            emitter.emit("work")

    def test_rejects_embedded_newlines(self):
        with (
            patch("random_examples.local_sockets.socket.create_connection"),
            LocalEmitter(("127.0.0.1", 8080)) as emitter,
            self.assertRaisesRegex(ValueError, "newline"),
        ):
            emitter.emit("first\nsecond")


@unittest.skipUnless(shutil.which("cc"), "A C compiler is required")
class CReceiverIntegrationTests(unittest.TestCase):
    def test_accepts_messages_from_python(self):
        compiler = shutil.which("cc")
        source = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "random_examples"
            / "receiver.c"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = Path(temporary_directory) / "receiver"
            assert compiler is not None
            subprocess.run(
                [
                    compiler,
                    "-std=c11",
                    "-D_POSIX_C_SOURCE=200809L",
                    str(source),
                    "-o",
                    str(executable),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            process = subprocess.Popen(
                [str(executable), "0"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            try:
                stdout = process.stdout
                assert stdout is not None
                startup_message = stdout.readline()
                self.assertTrue(startup_message.startswith("Listening on 127.0.0.1:"))
                port = int(startup_message.rsplit(":", maxsplit=1)[1])

                with LocalEmitter(("127.0.0.1", port)) as emitter:
                    emitter.emit("compile task")
                    emitter.emit("caf\u00e9")

                self.assertEqual(
                    [stdout.readline().rstrip("\n") for _ in range(2)],
                    ["compile task", "caf\u00e9"],
                )
            finally:
                process.terminate()
                process.wait(timeout=2)
                stdout.close()
                if process.stderr is not None:
                    process.stderr.close()


if __name__ == "__main__":
    unittest.main()
