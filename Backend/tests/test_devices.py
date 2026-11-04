import pytest

from aegismr.devices import Device, DeviceType


def test_create_router():
    router = Device(
        name="R1",
        device_type=DeviceType.ROUTER,
        ip_address="192.168.1.1",
    )
    assert router.name == "R1"
    assert router.device_type == DeviceType.ROUTER
    assert router.ip_address == "192.168.1.1"


def test_switch_without_ip():
    switch = Device(
        name="SW1",
        device_type=DeviceType.SWITCH,
    )
    assert switch.ip_address is None


def test_empty_name_rejected():
    with pytest.raises(ValueError):
        Device(
            name="",
            device_type=DeviceType.PC,
        )


def test_invalid_ip_rejected():
    with pytest.raises(ValueError):
        Device(
            name="PC1",
            device_type=DeviceType.PC,
            ip_address="999.1.1.1",
        )

def test_default_ports_by_type():
    """Each device should get a realistic number of ports by default, based on its type."""
    assert Device(name="PC1", device_type=DeviceType.PC).ports == 1
    assert Device(name="SW1", device_type=DeviceType.SWITCH).ports == 8
    assert Device(name="R1", device_type=DeviceType.ROUTER).ports == 4

def test_custom_ports():
    """The default can be overridden, e.g. for a 24-port switch."""
    switch = Device(name="SW2", device_type=DeviceType.SWITCH, ports=24)
    assert switch.ports == 24

def test_zero_ports_rejected():
    """A device with no ports must never be connected."""
    with pytest.raises(ValueError):
        Device(name="PC1", device_type=DeviceType.PC, ports=0)