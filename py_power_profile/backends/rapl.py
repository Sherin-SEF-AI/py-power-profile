"""RAPL backend for Intel/AMD processors."""

import time
from typing import Tuple

from .base import BaseBackend


class RAPLBackend(BaseBackend):
    """RAPL (Running Average Power Limit) backend for Intel/AMD processors."""

    def __init__(self) -> None:
        self._start_time: float = 0.0
        self._start_energy: float = 0.0
        self._rapl = None
        self._available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if pyRAPL is available and working."""
        try:
            import pyRAPL
            # Try to initialize RAPL
            pyRAPL.setup()
            return True
        except (ImportError, OSError, RuntimeError):
            return False

    def start(self) -> None:
        """Start energy measurement."""
        if not self._available:
            raise RuntimeError("RAPL backend not available")
        
        try:
            import pyRAPL
            self._start_time = time.time()
            self._start_energy = pyRAPL.RAPLMonitor.sample()
        except Exception as e:
            raise RuntimeError(f"Failed to start RAPL measurement: {e}")

    def stop(self) -> Tuple[float, float]:
        """Stop energy measurement and return (energy_mj, time_ms)."""
        if not self._available:
            raise RuntimeError("RAPL backend not available")
        
        try:
            import pyRAPL
            end_time = time.time()
            end_energy = pyRAPL.RAPLMonitor.sample()
            
            # Calculate energy difference in mJ
            energy_diff = end_energy - self._start_energy
            time_diff_ms = (end_time - self._start_time) * 1000
            
            return energy_diff, time_diff_ms
        except Exception as e:
            raise RuntimeError(f"Failed to stop RAPL measurement: {e}")

    def is_available(self) -> bool:
        """Check if this backend is available on the current system."""
        return self._available

    def get_name(self) -> str:
        """Get the name of this backend."""
        return "rapl" 