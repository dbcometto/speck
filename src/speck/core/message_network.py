# speck/core/message_network.py

class MessageNetwork:
    """World-level shared message network. Default behavior is instant FTL (ansible).
    Future: add latency, bandwidth limits, and origin tracking per entry."""

    def __init__(self):
        self._data: dict = {}

    def write(self, key: str, value) -> None:
        """Write a value to the network"""
        self._data[key] = value

    def read(self, key: str, default=None):
        """Read a value from the network"""
        return self._data.get(key, default)

    def clear(self, key: str) -> None:
        """Clear a key from the network"""
        self._data.pop(key, None)

    def keys(self) -> list:
        """List all keys"""
        return list(self._data.keys())

    def __contains__(self, key: str) -> bool:
        return key in self._data