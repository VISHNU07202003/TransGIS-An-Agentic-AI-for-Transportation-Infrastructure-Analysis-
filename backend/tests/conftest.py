"""Offline by default: provider access must be explicitly mocked in CI."""
import os
import socket

import httpx
import pytest


def pytest_collection_modifyitems(config, items):
    enabled = os.environ.get("TRANSGIS_RUN_LIVE_TESTS") == "1"
    for item in items:
        if item.get_closest_marker("live") and not enabled:
            item.add_marker(pytest.mark.skip(reason="Set TRANSGIS_RUN_LIVE_TESTS=1 to contact public providers"))


@pytest.fixture(autouse=True)
def prohibit_unmocked_network(request, monkeypatch):
    """Block HTTP/SQL/socket connections, including attempts swallowed by app code.

    ASGITransport and MockTransport are intentionally unaffected. Blocking the
    connection entry points avoids interfering with Windows asyncio socketpairs.
    """
    if request.node.get_closest_marker("live"):
        yield
        return
    attempted = []

    def blocked(*args, **kwargs):
        attempted.append("Unmocked network/database access")
        raise AssertionError("Offline test attempted network/database access; inject a fixture or mark live")

    async def async_blocked(*args, **kwargs):
        return blocked(*args, **kwargs)

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", blocked)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", async_blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
    import psycopg
    monkeypatch.setattr(psycopg.Connection, "connect", blocked)
    monkeypatch.setattr(psycopg.AsyncConnection, "connect", async_blocked)
    yield
    assert not attempted, "App swallowed an unmocked network/database attempt; this test is not isolated"


@pytest.fixture
def public_transport(monkeypatch):
    """Replace only outgoing HTTP transport; keep in-process ASGI clients real."""
    def install(handler):
        original_init = httpx.AsyncClient.__init__

        def init(client, *args, **kwargs):
            if "transport" not in kwargs:
                kwargs["transport"] = httpx.MockTransport(handler)
            original_init(client, *args, **kwargs)

        monkeypatch.setattr(httpx.AsyncClient, "__init__", init)
    return install
