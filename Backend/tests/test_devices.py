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
        