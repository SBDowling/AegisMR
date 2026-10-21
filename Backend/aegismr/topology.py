from collections import deque
from dataclasses import dataclass
from aegismr.devices import Device


@dataclass(frozen=True)
class Link:
    """A cable between two devices, identified by device name."""

    device_a: str
    device_b: str

    def __post_init__(self):
        if self.device_a == self.device_b:
            raise ValueError("A device cannot be linked to itself.")


class Topology:
    """A network made of devices and the links between them."""
    def __init__(self):
        self.devices: dict[str, Device] = {}
        self.links: list[Link] = []

    def add_device(self, device: Device) -> None:
        if device.name in self.devices:
            raise ValueError(f"Device '{device.name}' already exists.")
        self.devices[device.name] = device

    def add_link(self, device_a: str, device_b: str) -> Link:
        for name in (device_a, device_b):
            if name not in self.devices:
                raise ValueError(f"Unknown device '{name}'.")
        if device_b in self.neighbours(device_a):
            raise ValueError(f"'{device_a}' and '{device_b}' are already linked.")
        link = Link(device_a, device_b)
        self.links.append(link)
        return link

    def neighbours(self, name: str) -> list[str]:
        """Return the names of all devices directly linked to this one."""
        result = []
        for link in self.links:
            if link.device_a == name:
                result.append(link.device_b)
            elif link.device_b == name:
                result.append(link.device_a)
        return result

    def find_path(self, start: str, end: str) -> list[str] | None:
        """Return the shortest path of device names, or None if unreachable."""
        for name in (start, end):
            if name not in self.devices:
                raise ValueError(f"Unknown device '{name}'.")

        # Breadth-first search: explore one hop at a time, so the first
        # path that reaches the end is the shortest one
        queue = deque([[start]])
        visited = {start}
        while queue:
            path = queue.popleft()
            current = path[-1]
            if current == end:
                return path
            for neighbour in self.neighbours(current):
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(path + [neighbour])
        return None