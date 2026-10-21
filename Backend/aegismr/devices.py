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


@dataclass
class Device:
    """A single node in the network.

    See DeviceType for the supported kinds.
    """

    name: str
    device_type: DeviceType
    ip_address: str | None = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("Device name cannot be empty.")
        if self.ip_address is not None:
            # Raises ValueError for an invalid IPv4/IPv6 address
            ipaddress.ip_address(self.ip_address)