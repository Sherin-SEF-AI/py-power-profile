"""Mock backend for testing purposes."""

import time
from typing import Tuple

from .base import BaseBackend


class MockBackend(BaseBackend):
    """Mock backend that returns deterministic values for testing."""

    def __init__(self, energy_per_call_mj: float = 10.0) -> None:
        self._start_time: float = 0.0
        self._energy_per_call_mj = energy_per_call_mj

    def start(self) -> None:
        """Start energy measurement."""
        self._start_time = time.time()

    def stop(self) -> Tuple[float, float]:
        """Stop energy measurement and return (energy_mj, time_ms)."""
        end_time = time.time()
        time_diff_ms = (end_time - self._start_time) * 1000
        
        # Return fixed energy per call
        return self._energy_per_call_mj, time_diff_ms

    def is_available(self) -> bool:
        """Check if this backend is available on the current system."""
        return True

    def get_name(self) -> str:
        """Get the name of this backend."""
        return "mock" 