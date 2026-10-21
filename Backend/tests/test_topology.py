import pytest

from aegismr.devices import Device, DeviceType
from aegismr.topology import Link, Topology


@pytest.fixture
def small_network():
    """Build a sample network shared by the tests below.

    PC1 --- SW1 --- R1 --- SRV1      LT1 (not connected)
    """
    topology = Topology()
    topology.add_device(Device("PC1", DeviceType.PC, "192.168.1.10"))
    # Switches work at Layer 2, so SW1 has no IP address
    topology.add_device(Device("SW1", DeviceType.SWITCH))
    topology.add_device(Device("R1", DeviceType.ROUTER, "192.168.1.1"))
    # Server is on a different subnet, so traffic must go through R1
    topology.add_device(Device("SRV1", DeviceType.SERVER, "10.0.0.5"))
    # Laptop is added but never linked, to test unreachable devices
    topology.add_device(Device("LT1", DeviceType.LAPTOP, "192.168.1.20"))
    topology.add_link("PC1", "SW1")
    topology.add_link("SW1", "R1")
    topology.add_link("R1", "SRV1")
    return topology


# ----- Link validation -----

def test_link_to_self_rejected():
    """A device cannot be cabled to itself."""
    with pytest.raises(ValueError):
        Link("PC1", "PC1")


# ----- Adding devices and links -----

def test_duplicate_device_rejected(small_network):
    """Two devices cannot share a name, as names are used as IDs."""
    with pytest.raises(ValueError):
        small_network.add_device(Device("PC1", DeviceType.PC))


def test_link_to_unknown_device_rejected(small_network):
    """Links can only connect devices that exist in the topology."""
    with pytest.raises(ValueError):
        small_network.add_link("PC1", "NOPE")


def test_duplicate_link_rejected(small_network):
    """The same two devices cannot be linked twice."""
    # PC1-SW1 already exists; written in reverse to prove that
    # links have no direction
    with pytest.raises(ValueError):
        small_network.add_link("SW1", "PC1")


# ----- Querying the network -----

def test_neighbours(small_network):
    """A switch in the middle sees the devices on both sides of it."""
    # sorted() so the test doesn't depend on the order links were added
    assert sorted(small_network.neighbours("SW1")) == ["PC1", "R1"]


def test_find_path_pc_to_server(small_network):
    """The path from PC to server goes hop by hop via switch and router."""
    path = small_network.find_path("PC1", "SRV1")
    assert path == ["PC1", "SW1", "R1", "SRV1"]


def test_find_path_unreachable(small_network):
    """An unconnected device has no path, so None is returned."""
    assert small_network.find_path("PC1", "LT1") is None