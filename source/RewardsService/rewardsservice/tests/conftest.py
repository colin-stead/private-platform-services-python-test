"""
Pytest configuration: runs the service against the "Tests" database.

The server on localhost:7050 (docker) uses the "Rewards" database, so the tests start their own
copy of the Tornado app on TEST_PORT with DB_NAME=Tests. The environment is set up before anything
from the app is imported, because the handlers read it from database.py at import time.
"""
import asyncio
import os
import socket
import sys
import threading
import time

import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_DIR = os.path.dirname(TESTS_DIR)           # .../RewardsService/rewardsservice
PROJECT_DIR = os.path.dirname(SERVICE_DIR)         # .../RewardsService (database.py, load_mongo_data.py)

for path in (SERVICE_DIR, PROJECT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

# Must happen before importing database / the app. Pytest runs on the host, so Mongo is on localhost
# (the docker "mongodb" host name only resolves inside docker). MONGO_HOST / MONGO_PORT can be overridden.
os.environ["DB_NAME"] = "Tests"
os.environ.setdefault("MONGO_HOST", "localhost")

import database  # noqa: E402
import load_mongo_data  # noqa: E402

TEST_PORT = 7051
TEST_BASE_URL = f"http://localhost:{TEST_PORT}"


def _wait_for_port(port, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket() as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("localhost", port)) == 0:
                return
        time.sleep(0.1)
    raise RuntimeError(f"Test server did not start on port {port}")


@pytest.fixture(scope="session")
def db():
    """The "Tests" database."""
    return database.get_db()


@pytest.fixture(scope="session")
def base_url():
    return TEST_BASE_URL


@pytest.fixture(scope="session", autouse=True)
def test_server(db):
    """
    Seed the Tests DB with the rewards, serve the app on TEST_PORT for the session, and
    drop the customers collection when the session ends. Rewards are left in the Tests DB.
    """
    assert database.get_db().name == "Tests"  # never run the suite against the real data

    load_mongo_data.load(db)

    import tornado.httpserver
    import tornado.web
    from url_patterns import url_patterns

    started = threading.Event()
    state = {}

    def serve():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # Same routes as app.py, but without its debug/autoreload settings (app.py also builds the app at import time)
        server = tornado.httpserver.HTTPServer(tornado.web.Application(url_patterns))
        server.listen(TEST_PORT)
        state["loop"], state["server"] = loop, server
        started.set()
        loop.run_forever()
        server.stop()
        loop.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    assert started.wait(10), "Test server thread failed to start"
    _wait_for_port(TEST_PORT)

    yield

    state["loop"].call_soon_threadsafe(state["loop"].stop)
    thread.join(timeout=5)
    db.customers.drop()


@pytest.fixture(autouse=True)
def clean_customers(db, test_server):
    """Every test starts with, and leaves behind, an empty customers collection."""
    db.customers.delete_many({})
    yield
    db.customers.delete_many({})
