import ipaddress
from dataclasses import dataclass
from enum import Enum

class DeviceType(Enum):
    # Define device types
    ROUTER = "router"
    SWITCH = "switch"
    FIREWALL = "firewall"   
    PC = "pc"
    SERVER = "server"
    LAPTOP = "laptop"
    PHONE = "phone"
    INTERNET = "internet"

# Number of network ports each device type has by default.
DEFAULT_PORTS = {
    DeviceType.ROUTER: 4,
    DeviceType.SWITCH: 8,
    DeviceType.FIREWALL: 3,
    DeviceType.PC: 1,
    DeviceType.SERVER: 2,
    DeviceType.LAPTOP: 1,
    DeviceType.PHONE: 1,
    DeviceType.INTERNET: 4,
}

@dataclass
class Device:
    """A single node in the network.

    See DeviceType for the supported kinds.
    """

    name: str
    device_type: DeviceType
    ip_address: str | None = None
    ports: int | None = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("Device name cannot be empty.")
        if self.ip_address is not None:
            # Raises ValueError for an invalid IPv4/IPv6 address
            ipaddress.ip_address(self.ip_address)
        if self.ports is None:
            self.ports = DEFAULT_PORTS.get(self.device_type, 1)
        if self.ports < 1:
            raise ValueError("Device must have at least one port.")