import sys
import os
import socket
import threading
import dotenv
from validator import Validator


def handle_client(encoded_message: bytes, source_addr: str):
    message = encoded_message.decode("ascii")
    validator = Validator(message, source_addr)
    syslog_message = validator.validate_message()
    if syslog_message == message:
        print(f"[RECEIVED] {source_addr}: {syslog_message}")
    else:
        print(f"[RECEIVED, CORRECTED] {source_addr}:")
        print(f"Before: {message}")
        print(f"After: {syslog_message}")

    file = os.getenv("SYSLOG_FILE") or "syslog.log"
    with open(file, "a") as f:
        f.write(message)


def main():
    dotenv.load_dotenv()
    MAX_MESSAGE_LENGTH = 1024 # 1024 bytes
    # LISTEN_ADDRESS = socket.gethostbyname(socket.gethostname())
    LISTEN_ADDRESS = os.getenv("LISTEN_ADDRESS") or "127.0.0.1"
    LISTEN_PORT = 514

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((LISTEN_ADDRESS, LISTEN_PORT))
    print(f"Listening on {LISTEN_ADDRESS} UDP/{LISTEN_PORT}")

    while True:
        encoded_message, source_address = server.recvfrom(MAX_MESSAGE_LENGTH)
        thread = threading.Thread(target=handle_client, args=(encoded_message, source_address[0]))
        thread.start()


if __name__ == "__main__":
    main()