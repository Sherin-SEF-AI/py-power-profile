"""Base backend interface for energy measurement."""

from abc import ABC, abstractmethod
from typing import Tuple


class BaseBackend(ABC):
    """Abstract base class for energy measurement backends."""

    @abstractmethod
    def start(self) -> None:
        """Start energy measurement."""
        pass

    @abstractmethod
    def stop(self) -> Tuple[float, float]:
        """Stop energy measurement and return (energy_mj, time_ms)."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available on the current system."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this backend."""
        pass 