import socket
import threading

from src.random_examples import consumer


def test_tcp_listener_consumes_newline_delimited_messages(monkeypatch):
    received = []
    messages_received = threading.Event()

    def record_message(message: str) -> None:
        received.append(message)
        if len(received) == 2:
            messages_received.set()

    monkeypatch.setattr(consumer, "consume_message", record_message)
    server = consumer.ThreadedTCPServer(
        ("127.0.0.1", 0), consumer.LineMessageHandler
    )
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        with socket.create_connection(("127.0.0.1", server.server_address[1])) as client:
            client.sendall("hello\ncaf\u00e9\r\n".encode("utf-8"))

        assert messages_received.wait(timeout=2)
        assert received == ["hello", "caf\u00e9"]
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=2)
