import socket

import pytest


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def blocked_socket(*args, **kwargs):
        raise AssertionError("router_core tests must not use the network")

    monkeypatch.setattr(socket, "socket", blocked_socket)
