"""HWMON backend for ARM/Raspberry Pi power sensors."""

import glob
import time
from pathlib import Path
from typing import Tuple

from .base import BaseBackend


class HwmonBackend(BaseBackend):
    """HWMON backend for ARM/Raspberry Pi power sensors."""

    def __init__(self) -> None:
        self._start_time: float = 0.0
        self._start_power: float = 0.0
        self._power_file = None
        self._available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if hwmon power sensors are available."""
        try:
            # Look for power sensors in /sys/class/hwmon
            hwmon_dirs = glob.glob("/sys/class/hwmon/hwmon*")
            for hwmon_dir in hwmon_dirs:
                # Look for power files
                power_files = glob.glob(f"{hwmon_dir}/power*_input")
                if power_files:
                    self._power_file = power_files[0]
                    return True
            return False
        except Exception:
            return False

    def _read_power(self) -> float:
        """Read current power consumption in mW."""
        if not self._power_file:
            return 0.0
        
        try:
            with open(self._power_file, "r") as f:
                power_mw = float(f.read().strip())
                return power_mw
        except Exception:
            return 0.0

    def start(self) -> None:
        """Start energy measurement."""
        if not self._available:
            raise RuntimeError("HWMON backend not available")
        
        self._start_time = time.time()
        self._start_power = self._read_power()

    def stop(self) -> Tuple[float, float]:
        """Stop energy measurement and return (energy_mj, time_ms)."""
        if not self._available:
            raise RuntimeError("HWMON backend not available")
        
        end_time = time.time()
        end_power = self._read_power()
        
        # Calculate average power and energy
        avg_power_mw = (self._start_power + end_power) / 2
        time_diff_s = end_time - self._start_time
        
        # Convert to mJ: power_mw * time_s * 1000
        energy_mj = avg_power_mw * time_diff_s * 1000
        time_diff_ms = time_diff_s * 1000
        
        return energy_mj, time_diff_ms

    def is_available(self) -> bool:
        """Check if this backend is available on the current system."""
        return self._available

    def get_name(self) -> str:
        """Get the name of this backend."""
        return "hwmon" 