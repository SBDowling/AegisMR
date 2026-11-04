import json

from scapy.layers.inet import ICMP, IP
from scapy.layers.l2 import Ether

from aegismr.packets import Hop
from aegismr.topology import Topology

# The only requests Unity is allowed to send; anything else is rejected
REQUEST_TYPES = {"get_topology", "ping"}


def topology_message(topology: Topology) -> dict:
    """Describe every device and link, so Unity can build the scene."""
    return {
        "type": "topology",
        "devices": [
            {
                "name": device.name,
                "device_type": device.device_type.value,
                "ip_address": device.ip_address,
                "mac_address": device.mac_address,
                "ports": device.ports,
            }
            for device in topology.devices.values()
        ],
        "links": [
            {"device_a": link.device_a, "device_b": link.device_b}
            for link in topology.links
        ],
    }


def hop_to_dict(hop: Hop) -> dict:
    """Copy the fields learners need from one hop's Scapy packet."""
    packet = hop.packet
    return {
        "from_device": hop.from_device,
        "to_device": hop.to_device,
        "ether": {"src": packet[Ether].src, "dst": packet[Ether].dst},
        "ip": {
            "src": packet[IP].src,
            "dst": packet[IP].dst,
            "ttl": packet[IP].ttl,
        },
        "icmp": {"type": packet[ICMP].type},
    }


def ping_result_message(source: str, destination: str, hops: list[Hop]) -> dict:
    """Describe a ping's whole journey, one entry per link."""
    return {
        "type": "ping_result",
        "source": source,
        "destination": destination,
        "hops": [hop_to_dict(hop) for hop in hops],
    }


def error_message(reason: str) -> dict:
    """Tell Unity a request could not be carried out."""
    return {"type": "error", "reason": reason}


def parse_request(text: str) -> dict:
    """Turn a JSON request from Unity into a dict, or raise ValueError.

    Only known request types with the right fields are accepted.
    """
    # json.JSONDecodeError is a kind of ValueError
    request = json.loads(text)
    if not isinstance(request, dict):
        raise ValueError("A request must be a JSON object.")
    if request.get("type") not in REQUEST_TYPES:
        raise ValueError(f"Unknown request type '{request.get('type')}'.")
    if request["type"] == "ping":
        for field in ("source", "destination"):
            if not isinstance(request.get(field), str):
                raise ValueError(f"A ping needs a '{field}' device name.")
    return request