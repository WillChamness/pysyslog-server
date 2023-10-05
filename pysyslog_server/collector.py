import sys
import os
import socket
import threading
import dotenv
import pymongo
from .validator import Validator
from .parser import Parser


def handle_client(encoded_message: bytes, source_addr: str):
    message = encoded_message.decode("ascii").strip() 
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

    use_db = os.getenv("SYSLOG_USE_DB") or "no"
    if(use_db.lower() == "yes"):
        _save_to_db(syslog_message)


def _save_to_db(syslog):
    parser = Parser(syslog)
    parsed_syslog = parser.parse()

    mongo_uri = os.getenv("MONGODB_URI") 
    mongo_db_name = os.getenv("MONGODB_DBNAME") 
    mongo_collection_name = os.getenv("MONGODB_COLLECTION") 

    with pymongo.MongoClient(mongo_uri) as conn:
        db = conn.mongo_db_name
        logs = db.mongo_collection_name

        new_log = logs.insert_one(parsed_syslog)
        print(f"[INSERTED] Created log ID: {new_log.inserted_id}")


def start():
    dotenv.load_dotenv()
    MAX_MESSAGE_LENGTH = 1024 # 1024 bytes
    LISTEN_ADDRESS = os.getenv("SYSLOG_LISTEN_ADDRESS") or "127.0.0.1"
    if(os.getenv("SYSLOG_LISTEN_PORT")):
        LISTEN_PORT = int(os.getenv("SYSLOG_LISTEN_PORT"))
    else:
        LISTEN_PORT = 514

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((LISTEN_ADDRESS, LISTEN_PORT))
    print(f"Listening on {LISTEN_ADDRESS} UDP/{LISTEN_PORT}\n\n")

    while True:
        encoded_message, source_address = server.recvfrom(MAX_MESSAGE_LENGTH)
        thread = threading.Thread(target=handle_client, args=(encoded_message, source_address[0]))
        thread.start()


if __name__ == "__main__":
    start()