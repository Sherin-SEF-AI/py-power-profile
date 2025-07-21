"""PSUTIL estimation backend as universal fallback."""

import time
from typing import Tuple

import psutil

from .base import BaseBackend
from ..config import config


class PsutilEstBackend(BaseBackend):
    """PSUTIL estimation backend using CPU usage and TDP."""

    def __init__(self) -> None:
        self._start_time: float = 0.0
        self._start_cpu_percent: float = 0.0
        self._tdp_watts = config.tdp_watts

    def start(self) -> None:
        """Start energy measurement."""
        self._start_time = time.time()
        # Get initial CPU usage
        self._start_cpu_percent = psutil.cpu_percent(interval=0.1)

    def stop(self) -> Tuple[float, float]:
        """Stop energy measurement and return (energy_mj, time_ms)."""
        end_time = time.time()
        # Get final CPU usage
        end_cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Calculate average CPU usage
        avg_cpu_percent = (self._start_cpu_percent + end_cpu_percent) / 2
        
        # Estimate power consumption: TDP * CPU usage percentage
        power_watts = (self._tdp_watts * avg_cpu_percent) / 100
        
        # Calculate time difference
        time_diff_s = end_time - self._start_time
        
        # Convert to mJ: power_watts * time_s * 1000
        energy_mj = power_watts * time_diff_s * 1000
        time_diff_ms = time_diff_s * 1000
        
        return energy_mj, time_diff_ms

    def is_available(self) -> bool:
        """Check if this backend is available on the current system."""
        return True  # psutil is always available

    def get_name(self) -> str:
        """Get the name of this backend."""
        return "psutil_est" 