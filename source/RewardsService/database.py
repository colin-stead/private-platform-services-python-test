"""
Database configuration shared by the service, the data loader and the tests.

Connection settings live in os.environ so they can be changed without touching code
(the tests set DB_NAME=Tests before the app is imported):

    MONGO_HOST  host name of the MongoDB server   (default: "mongodb", the docker compose service)
    MONGO_PORT  port of the MongoDB server        (default: 27017)
    DB_NAME     database the service reads/writes (default: "Rewards")
"""
import os

from pymongo import MongoClient

os.environ.setdefault("MONGO_HOST", "mongodb")
os.environ.setdefault("MONGO_PORT", "27017")
os.environ.setdefault("DB_NAME", "Rewards")
os.environ.setdefault("URI", "http://localhost:7050")

_client = None


def get_client():
    """
    Get the shared MongoClient, creating it on first use.

    Returns:
        MongoClient: A client for MONGO_HOST:MONGO_PORT
    """
    global _client
    if _client is None:
        _client = MongoClient(os.environ["MONGO_HOST"], int(os.environ["MONGO_PORT"]))
    return _client


def get_db():
    """
    Get the database named by DB_NAME. DB_NAME is read on every call so changes to os.environ are honoured.

    Returns:
        Database: The active database ("Rewards" by default, "Tests" under pytest)
    """
    return get_client()[os.environ["DB_NAME"]]
