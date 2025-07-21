"""Function tracing and energy measurement."""

import sys
import time
from collections import defaultdict
from typing import Any, Callable, Dict, Optional, Tuple

from .backends import BaseBackend
from .config import config


class FunctionStats:
    """Statistics for a single function."""

    def __init__(self) -> None:
        self.calls = 0
        self.total_energy_mj = 0.0
        self.total_time_ms = 0.0
        self.min_energy_mj = float('inf')
        self.max_energy_mj = 0.0

    def update(self, energy_mj: float, time_ms: float) -> None:
        """Update statistics with new measurement."""
        self.calls += 1
        self.total_energy_mj += energy_mj
        self.total_time_ms += time_ms
        self.min_energy_mj = min(self.min_energy_mj, energy_mj)
        self.max_energy_mj = max(self.max_energy_mj, energy_mj)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "calls": self.calls,
            "total_energy_mj": self.total_energy_mj,
            "total_time_ms": self.total_time_ms,
            "avg_energy_mj": self.total_energy_mj / self.calls if self.calls > 0 else 0.0,
            "avg_time_ms": self.total_time_ms / self.calls if self.calls > 0 else 0.0,
            "min_energy_mj": self.min_energy_mj if self.min_energy_mj != float('inf') else 0.0,
            "max_energy_mj": self.max_energy_mj,
        }


class EnergyTracer:
    """Tracer that measures energy consumption of function calls."""

    def __init__(self, backend: BaseBackend, line_level: bool = False) -> None:
        self.backend = backend
        self.line_level = line_level
        self.stats: Dict[str, FunctionStats] = defaultdict(FunctionStats)
        self.call_stack: list = []
        self.original_trace = None

    def _get_function_key(self, frame) -> str:
        """Generate a unique key for a function."""
        filename = frame.f_code.co_filename
        funcname = frame.f_code.co_name
        
        # Skip if file should be ignored
        if config.should_ignore(filename):
            return ""
        
        return f"{filename}:{funcname}"

    def _trace_callback(self, frame, event: str, arg) -> Optional[Callable]:
        """Trace callback for sys.settrace."""
        if event == "call":
            func_key = self._get_function_key(frame)
            if func_key:  # Only trace if not ignored
                self.call_stack.append(func_key)
                self.backend.start()
        
        elif event == "return":
            if self.call_stack:
                func_key = self.call_stack.pop()
                try:
                    energy_mj, time_ms = self.backend.stop()
                    self.stats[func_key].update(energy_mj, time_ms)
                except Exception as e:
                    # Log error but continue tracing
                    print(f"Warning: Energy measurement failed for {func_key}: {e}", file=sys.stderr)
        
        elif event == "line" and self.line_level:
            # Line-level tracing (coarser accuracy)
            if self.call_stack:
                func_key = self.call_stack[-1]
                try:
                    energy_mj, time_ms = self.backend.stop()
                    self.backend.start()  # Restart for next line
                    self.stats[func_key].update(energy_mj, time_ms)
                except Exception as e:
                    print(f"Warning: Line-level energy measurement failed: {e}", file=sys.stderr)
        
        return self._trace_callback

    def start(self) -> None:
        """Start tracing."""
        self.original_trace = sys.gettrace()
        sys.settrace(self._trace_callback)

    def stop(self) -> Dict[str, FunctionStats]:
        """Stop tracing and return collected statistics."""
        sys.settrace(self.original_trace)
        return dict(self.stats)

    def get_results(self) -> Dict[str, Any]:
        """Get results in a format suitable for JSON serialization."""
        results = {
            "metadata": {
                "backend": self.backend.get_name(),
                "line_level": self.line_level,
                "timestamp": time.time(),
            },
            "functions": {}
        }
        
        total_energy = 0.0
        total_time = 0.0
        
        for func_key, stats in self.stats.items():
            results["functions"][func_key] = stats.to_dict()
            total_energy += stats.total_energy_mj
            total_time += stats.total_time_ms
        
        results["summary"] = {
            "total_energy_mj": total_energy,
            "total_time_ms": total_time,
            "function_count": len(self.stats),
        }
        
        return results 