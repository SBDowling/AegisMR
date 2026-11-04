import json

from websockets.asyncio.client import connect
from websockets.asyncio.server import serve

from aegismr.server import demo_network, handle_request, make_handler


# ----- Replies, without a network connection -----

def test_get_topology_request(small_network):
    reply = handle_request(small_network, '{"type": "get_topology"}')
    assert reply["type"] == "topology"


def test_ping_request(small_network):
    text = '{"type": "ping", "source": "PC1", "destination": "SRV1"}'
    reply = handle_request(small_network, text)
    assert reply["type"] == "ping_result"
    assert len(reply["hops"]) == 3


def test_bad_request_gets_error_reply(small_network):
    """The server answers with an error instead of crashing."""
    reply = handle_request(small_network, '{"type": "delete_everything"}')
    assert reply["type"] == "error"


def test_ping_to_unknown_device_gets_error_reply(small_network):
    text = '{"type": "ping", "source": "PC1", "destination": "PC99"}'
    reply = handle_request(small_network, text)
    assert reply["type"] == "error"


def test_demo_network_is_connected():
    """The network the server starts with can ping end to end."""
    assert demo_network().find_path("PC1", "SRV1") is not None


# ----- A real WebSocket conversation -----

async def test_client_conversation(small_network):
    """Start a real server, connect a client, and exchange messages."""
    # Port 0 asks the computer for any free port, so tests never clash
    async with serve(make_handler(small_network), "localhost", 0) as server:
        port = server.sockets[0].getsockname()[1]
        async with connect(f"ws://localhost:{port}") as client:
            # The server sends the topology as soon as we connect
            welcome = json.loads(await client.recv())
            assert welcome["type"] == "topology"

            # Ask for a ping and check the reply
            await client.send(json.dumps(
                {"type": "ping", "source": "PC1", "destination": "SRV1"}
            ))
            reply = json.loads(await client.recv())
            assert reply["type"] == "ping_result"
            assert reply["hops"][0]["from_device"] == "PC1"

            # A bad request gets an error, and the connection stays open
            await client.send("not json")
            assert json.loads(await client.recv())["type"] == "error"