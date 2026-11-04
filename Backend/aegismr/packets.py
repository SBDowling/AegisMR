from dataclasses import dataclass

from scapy.layers.inet import ICMP, IP
from scapy.layers.l2 import Ether
from scapy.packet import Packet

from aegismr.devices import DeviceType
from aegismr.topology import Topology

# Starting time-to-live for new packets, as used by most operating systems
DEFAULT_TTL = 64

# Devices that forward frames without changing their MAC addresses
LAYER_2_DEVICES = {DeviceType.SWITCH}


@dataclass
class Hop:
    """One step of a packet's journey, across a single link."""

    from_device: str
    to_device: str
    packet: Packet


def ping_hops(topology: Topology, source: str, destination: str) -> list[Hop]:
    """Build the ICMP echo request seen on each link from source to destination.

    Every address comes from the simulated devices, so Scapy never fills
    in details from the real computer. Nothing is sent on any network.
    """
    path = topology.find_path(source, destination)
    if path is None:
        raise ValueError(f"No path from '{source}' to '{destination}'.")

    for name in (source, destination):
        if topology.devices[name].ip_address is None:
            raise ValueError(f"'{name}' needs an IP address for a ping.")

    # Positions on the path where the frame is rebuilt (hosts and routers);
    # switches pass frames along unchanged
    stops = [
        i for i, name in enumerate(path)
        if topology.devices[name].device_type not in LAYER_2_DEVICES
    ]
    for i in stops:
        if topology.devices[path[i]].mac_address is None:
            raise ValueError(f"'{path[i]}' needs a MAC address.")

    src = topology.devices[source]
    dst = topology.devices[destination]
    hops = []
    for i in range(len(path) - 1):
        # The frame on this link runs from the last stop to the next stop
        sender = topology.devices[path[max(p for p in stops if p <= i)]]
        receiver = topology.devices[path[min(p for p in stops if p > i)]]
        # Each router passed so far lowers the TTL by one
        routers_passed = len([p for p in stops if 0 < p <= i])
        packet = (
            Ether(src=sender.mac_address, dst=receiver.mac_address)
            / IP(
                src=src.ip_address,
                dst=dst.ip_address,
                ttl=DEFAULT_TTL - routers_passed,
            )
            / ICMP(type="echo-request")
        )
        hops.append(Hop(path[i], path[i + 1], packet))
    return hops