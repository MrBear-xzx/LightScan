from abc import ABC, abstractmethod


class DiscoveryPlugin(ABC):
    @abstractmethod
    def discover(self, targets: list[str], policy: dict) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> dict:
        raise NotImplementedError


class ScannerPlugin(ABC):
    @abstractmethod
    def scan(self, asset: dict, policy: dict) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw_result: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> dict:
        raise NotImplementedError
