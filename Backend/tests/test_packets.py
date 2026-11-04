import socket
import uuid

import pytest
from scapy.layers.inet import ICMP, IP
from scapy.layers.l2 import Ether

from aegismr.packets import DEFAULT_TTL, ping_hops


def real_addresses():
    """Return this computer's real IP and MAC addresses."""
    ips = set(socket.gethostbyname_ex(socket.gethostname())[2])
    ips.add("127.0.0.1")
    mac_int = uuid.getnode()
    mac = ":".join(
        f"{(mac_int >> shift) & 0xff:02x}" for shift in range(40, -1, -8)
    )
    return ips, {mac}


# ----- The journey -----

def test_hops_follow_the_path(small_network):
    """There is one hop per cable, in order from PC to server."""
    hops = ping_hops(small_network, "PC1", "SRV1")
    steps = [(hop.from_device, hop.to_device) for hop in hops]
    assert steps == [("PC1", "SW1"), ("SW1", "R1"), ("R1", "SRV1")]


def test_packet_is_an_echo_request(small_network):
    """A ping is an ICMP echo request (ICMP type 8)."""
    hop = ping_hops(small_network, "PC1", "SRV1")[0]
    assert hop.packet[ICMP].type == 8


# ----- Networking rules shown to learners -----

def test_ip_addresses_stay_the_same_end_to_end(small_network):
    """IP addresses identify the original sender and final receiver."""
    for hop in ping_hops(small_network, "PC1", "SRV1"):
        assert hop.packet[IP].src == "192.168.1.10"
        assert hop.packet[IP].dst == "10.0.0.5"


def test_mac_addresses_change_only_at_the_router(small_network):
    """Switches forward frames unchanged; routers build new ones."""
    devices = small_network.devices
    hops = ping_hops(small_network, "PC1", "SRV1")
    # PC1 -> SW1 and SW1 -> R1 carry the same frame, addressed to the router
    for hop in hops[:2]:
        assert hop.packet[Ether].src == devices["PC1"].mac_address
        assert hop.packet[Ether].dst == devices["R1"].mac_address
    # The router creates a new frame for the server's network
    assert hops[2].packet[Ether].src == devices["R1"].mac_address
    assert hops[2].packet[Ether].dst == devices["SRV1"].mac_address


def test_ttl_drops_after_each_router(small_network):
    """TTL starts at 64 and the router lowers it by one."""
    ttls = [hop.packet[IP].ttl for hop in ping_hops(small_network, "PC1", "SRV1")]
    assert ttls == [DEFAULT_TTL, DEFAULT_TTL, DEFAULT_TTL - 1]


# ----- Invalid requests -----

def test_unreachable_destination_rejected(small_network):
    """LT1 has no cable, so no ping can reach it."""
    with pytest.raises(ValueError):
        ping_hops(small_network, "PC1", "LT1")


def test_device_without_ip_rejected(small_network):
    """SW1 has no IP address, so it cannot be pinged."""
    with pytest.raises(ValueError):
        ping_hops(small_network, "PC1", "SW1")


# ----- Safety: no real data -----

def test_packets_contain_only_simulated_addresses(small_network):
    """Every address in every packet comes from the fake network."""
    devices = small_network.devices.values()
    fake_ips = {d.ip_address for d in devices if d.ip_address}
    fake_macs = {d.mac_address for d in devices if d.mac_address}
    real_ips, real_macs = real_addresses()

    for hop in ping_hops(small_network, "PC1", "SRV1"):
        # Converting to bytes forces Scapy to fill in every field
        final = Ether(bytes(hop.packet))

        # Allowlist: only addresses invented for the simulation
        assert final[IP].src in fake_ips
        assert final[IP].dst in fake_ips
        assert final[Ether].src in fake_macs
        assert final[Ether].dst in fake_macs

        # Denylist: nothing from this real computer
        assert final[IP].src not in real_ips
        assert final[Ether].src not in real_macs