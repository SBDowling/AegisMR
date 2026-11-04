import asyncio
import json

from websockets.asyncio.server import ServerConnection, serve

from aegismr.devices import Device, DeviceType
from aegismr.messages import (
    error_message,
    parse_request,
    ping_result_message,
    topology_message,
)
from aegismr.packets import ping_hops
from aegismr.topology import Topology

# localhost means only programs on this computer can connect.
# Change to "0.0.0.0" only on a trusted network, e.g. your own hotspot.
HOST = "localhost"
PORT = 8765

# Largest message accepted from a client, in bytes; real requests are tiny
MAX_MESSAGE_SIZE = 64 * 1024


def demo_network() -> Topology:
    """Build the sample network the server starts with.

    Every address is invented: private IPs and locally administered MACs.
    """
    topology = Topology()
    topology.add_device(Device("PC1", DeviceType.PC, "192.168.1.10", "02:00:00:00:00:01"))
    topology.add_device(Device("SW1", DeviceType.SWITCH, mac_address="02:00:00:00:00:02"))
    topology.add_device(Device("R1", DeviceType.ROUTER, "192.168.1.1", "02:00:00:00:00:03"))
    topology.add_device(Device("SRV1", DeviceType.SERVER, "10.0.0.5", "02:00:00:00:00:04"))
    topology.add_link("PC1", "SW1")
    topology.add_link("SW1", "R1")
    topology.add_link("R1", "SRV1")
    return topology


def handle_request(topology: Topology, text: str) -> dict:
    """Work out the reply to one request from Unity.

    Bad requests get an error message instead of crashing the server.
    """
    try:
        request = parse_request(text)
        if request["type"] == "get_topology":
            return topology_message(topology)
        # The only other allowed type is "ping"
        hops = ping_hops(topology, request["source"], request["destination"])
        return ping_result_message(request["source"], request["destination"], hops)
    except ValueError as error:
        return error_message(str(error))


def make_handler(topology: Topology):
    """Create the function that talks to each connected client."""

    async def handler(websocket: ServerConnection) -> None:
        # Send the network straight away so Unity can build the scene
        await websocket.send(json.dumps(topology_message(topology)))
        # Then answer each request until the client disconnects
        async for text in websocket:
            reply = handle_request(topology, text)
            await websocket.send(json.dumps(reply))

    return handler


async def main() -> None:
    topology = demo_network()
    async with serve(
        make_handler(topology), HOST, PORT, max_size=MAX_MESSAGE_SIZE
    ) as server:
        print(f"AegisMR backend running on ws://{HOST}:{PORT} (Ctrl+C to stop)")
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped.")