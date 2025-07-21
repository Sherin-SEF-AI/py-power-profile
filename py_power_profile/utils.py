"""Utility functions for py-power-profile."""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from .backends import (
    BaseBackend,
    RAPLBackend,
    HwmonBackend,
    PsutilEstBackend,
    MockBackend,
)


def get_backend(backend_name: str) -> BaseBackend:
    """Get the appropriate backend based on name."""
    if backend_name == "auto":
        return get_auto_backend()
    elif backend_name == "rapl":
        return RAPLBackend()
    elif backend_name == "hwmon":
        return HwmonBackend()
    elif backend_name == "psutil_est":
        return PsutilEstBackend()
    elif backend_name == "mock":
        return MockBackend()
    else:
        raise ValueError(f"Unknown backend: {backend_name}")


def get_auto_backend() -> BaseBackend:
    """Automatically select the best available backend."""
    # Try backends in order of preference
    backends = [
        ("rapl", RAPLBackend),
        ("hwmon", HwmonBackend),
        ("psutil_est", PsutilEstBackend),
    ]
    
    for name, backend_class in backends:
        try:
            backend = backend_class()
            if backend.is_available():
                print(f"Using {name} backend", file=sys.stderr)
                return backend
        except Exception:
            continue
    
    # Fallback to psutil estimation
    print("Using psutil_est backend (fallback)", file=sys.stderr)
    return PsutilEstBackend()


def load_results(file_path: str) -> Dict[str, Any]:
    """Load results from JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Results file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in results file: {e}")


def save_results(results: Dict[str, Any], file_path: str) -> None:
    """Save results to JSON file."""
    with open(file_path, "w") as f:
        json.dump(results, f, indent=2)


def run_script(script_path: str, args: list = None) -> None:
    """Run a Python script with the given arguments."""
    if args is None:
        args = []
    
    # Add the script path to sys.path so it can be imported
    script_dir = Path(script_path).parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    
    # Read and execute the script
    with open(script_path, "r") as f:
        script_code = f.read()
    
    # Set up the script's namespace
    script_globals = {
        "__name__": "__main__",
        "__file__": script_path,
    }
    
    # Execute the script
    exec(script_code, script_globals)


def format_energy(energy_mj: float) -> str:
    """Format energy value with appropriate units."""
    if energy_mj >= 1000:
        return f"{energy_mj/1000:.2f} J"
    else:
        return f"{energy_mj:.1f} mJ"


def format_time(time_ms: float) -> str:
    """Format time value with appropriate units."""
    if time_ms >= 1000:
        return f"{time_ms/1000:.2f} s"
    else:
        return f"{time_ms:.1f} ms" 