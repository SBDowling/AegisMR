import json

import pytest

from aegismr.messages import (
    error_message,
    parse_request,
    ping_result_message,
    topology_message,
)
from aegismr.packets import ping_hops


# ----- Topology message -----

def test_topology_message_lists_devices_and_links(small_network):
    """Unity receives every device and every cable."""
    message = topology_message(small_network)
    names = {device["name"] for device in message["devices"]}
    assert message["type"] == "topology"
    assert names == {"PC1", "SW1", "R1", "SRV1", "LT1"}
    assert len(message["links"]) == 3


def test_topology_message_device_fields(small_network):
    """Device types are sent as plain text, not Python enums."""
    devices = {d["name"]: d for d in topology_message(small_network)["devices"]}
    assert devices["R1"] == {
        "name": "R1",
        "device_type": "router",
        "ip_address": "192.168.1.1",
        "mac_address": "02:00:00:00:00:03",
        "ports": 4,
    }
    # A switch has no IP address, which becomes null in JSON
    assert devices["SW1"]["ip_address"] is None


# ----- Ping result message -----

def test_ping_result_has_one_entry_per_hop(small_network):
    """Each hop shows the cable and the packet's addresses."""
    hops = ping_hops(small_network, "PC1", "SRV1")
    message = ping_result_message("PC1", "SRV1", hops)
    assert message["type"] == "ping_result"
    assert len(message["hops"]) == 3
    last = message["hops"][2]
    assert (last["from_device"], last["to_device"]) == ("R1", "SRV1")
    assert last["ether"] == {"src": "02:00:00:00:00:03", "dst": "02:00:00:00:00:04"}
    assert last["ip"] == {"src": "192.168.1.10", "dst": "10.0.0.5", "ttl": 63}
    assert last["icmp"] == {"type": 8}


def test_messages_convert_to_json(small_network):
    """Every message must survive a round trip through JSON text."""
    hops = ping_hops(small_network, "PC1", "SRV1")
    for message in (
        topology_message(small_network),
        ping_result_message("PC1", "SRV1", hops),
        error_message("Something went wrong."),
    ):
        assert json.loads(json.dumps(message)) == message


# ----- Requests from Unity -----

def test_parse_get_topology_request():
    assert parse_request('{"type": "get_topology"}') == {"type": "get_topology"}


def test_parse_ping_request():
    text = '{"type": "ping", "source": "PC1", "destination": "SRV1"}'
    assert parse_request(text)["destination"] == "SRV1"


@pytest.mark.parametrize(
    "text",
    [
        "not json at all",                       # Not valid JSON
        '["ping"]',                              # JSON, but not an object
        '{"type": "delete_everything"}',         # Unknown request type
        '{"source": "PC1"}',                     # No type at all
        '{"type": "ping", "source": "PC1"}',     # Ping missing destination
        '{"type": "ping", "source": 5, "destination": "SRV1"}',  # Wrong type
    ],
)
def test_bad_requests_rejected(text):
    """Anything that is not a known, complete request is refused."""
    with pytest.raises(ValueError):
        parse_request(text)