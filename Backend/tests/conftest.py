import pytest

from aegismr.devices import Device, DeviceType
from aegismr.topology import Topology


@pytest.fixture
def small_network():
    """Build a sample network shared by all test files.

    PC1 --- SW1 --- R1 --- SRV1      LT1 (not connected)

    MACs starting 02: are "locally administered", a range that never
    belongs to a real manufacturer, so they cannot match real hardware.
    """
    topology = Topology()
    topology.add_device(
        Device("PC1", DeviceType.PC, "192.168.1.10", "02:00:00:00:00:01")
    )
    # Switches work at Layer 2, so SW1 has no IP address
    topology.add_device(
        Device("SW1", DeviceType.SWITCH, mac_address="02:00:00:00:00:02")
    )
    topology.add_device(
        Device("R1", DeviceType.ROUTER, "192.168.1.1", "02:00:00:00:00:03")
    )
    # Server is on a different subnet, so traffic must go through R1
    topology.add_device(
        Device("SRV1", DeviceType.SERVER, "10.0.0.5", "02:00:00:00:00:04")
    )
    # Laptop is added but never linked, to test unreachable devices
    topology.add_device(
        Device("LT1", DeviceType.LAPTOP, "192.168.1.20", "02:00:00:00:00:05")
    )
    topology.add_link("PC1", "SW1")
    topology.add_link("SW1", "R1")
    topology.add_link("R1", "SRV1")
    return topology