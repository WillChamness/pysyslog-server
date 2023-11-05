"""
Contains the functions to start Syslog and handle incoming 
Syslog messages.
"""
import sys
import os
import socket
import threading
import dotenv
import pymongo
from .validator import Validator
from .parser import Parser


def _handle_client(encoded_message: bytes, source_addr: str):
    """
    Handles the Syslog device's incoming message.

    Performs validation/correction of the message.

    Args:
        encoded_message (bytes): The ASCII-encoded message.
        source_addr (str): The IP address of the client.
    """
    message: str = encoded_message.decode("ascii").strip() 
    validator: Validator = Validator(message, source_addr)
    syslog_message: str = validator.validate_message()

    if syslog_message == message:
        print(f"[RECEIVED] {source_addr}: {syslog_message}")
    else:
        print(f"[RECEIVED, CORRECTED] {source_addr}:")
        print(f"\tBefore: {message}")
        print(f"\tAfter: {syslog_message}")

    file: str = os.getenv("SYSLOG_FILE") or "syslog.log"
    with open("./syslog/" + file, "a") as f:
        f.write(f"{syslog_message}\n")

    use_db: str = os.getenv("SYSLOG_USE_DB") or "no"
    if(use_db.lower() == "yes"):
        _save_to_db(syslog_message)


def _save_to_db(syslog: str):
    """
    Saves the syslog message to a MongoDB database.

    Performs parsing to split the message into facility, severity,
    etc.

    Args:
        syslog (str): The valid Syslog message.
    """
    parser: Parser = Parser(syslog)
    parsed_syslog: dict = parser.parse()

    mongo_uri: str = os.getenv("MONGODB_URI") 
    mongo_db_name: str = os.getenv("MONGODB_DBNAME") 
    mongo_collection_name: str = os.getenv("MONGODB_COLLECTION") 

    with pymongo.MongoClient(mongo_uri) as conn:
        db = conn[mongo_db_name]
        logs = db[mongo_collection_name]

        new_log = logs.insert_one(parsed_syslog)
        print(f"[INSERTED] Created log ID: {new_log.inserted_id}")


def start():
    """Begins listening for Syslog messages."""
    dotenv.load_dotenv()
    syslog_dir: str = "./syslog/"
    if not os.path.isdir(syslog_dir):
        os.makedirs(syslog_dir)
    MAX_MESSAGE_LENGTH: int = 1024 # 1024 bytes
    LISTEN_ADDRESS: str = os.getenv("SYSLOG_LISTEN_ADDRESS") or "127.0.0.1"
    if(os.getenv("SYSLOG_LISTEN_PORT")):
        LISTEN_PORT = int(os.getenv("SYSLOG_LISTEN_PORT"))
    else:
        LISTEN_PORT = 514

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((LISTEN_ADDRESS, LISTEN_PORT))
    print(f"Listening on {LISTEN_ADDRESS} UDP/{LISTEN_PORT}\n\n")

    while True:
        encoded_message, source_address = server.recvfrom(MAX_MESSAGE_LENGTH)
        thread = threading.Thread(target=_handle_client, args=(encoded_message, source_address[0]))
        thread.start()


if __name__ == "__main__":
    start()