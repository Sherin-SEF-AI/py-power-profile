"""Configuration management for py-power-profile."""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib


class Config:
    """Configuration manager for py-power-profile."""

    def __init__(self) -> None:
        self.backend = "auto"
        self.tdp_watts = 15.0
        self.energy_budget_mj = 1000.0
        self.ignore_patterns: List[str] = ["tests/*"]
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from pyproject.toml and .pypowerprofile."""
        config_files = [
            Path("pyproject.toml"),
            Path(".pypowerprofile"),
            Path.home() / ".pypowerprofile",
        ]

        for config_file in config_files:
            if config_file.exists():
                self._load_from_file(config_file)

        # Environment variables override file config
        if os.getenv("PY_POWER_BACKEND"):
            self.backend = os.getenv("PY_POWER_BACKEND", "auto")
        if os.getenv("PY_POWER_TDP_WATTS"):
            self.tdp_watts = float(os.getenv("PY_POWER_TDP_WATTS", "15.0"))
        if os.getenv("PY_POWER_ENERGY_BUDGET_MJ"):
            self.energy_budget_mj = float(os.getenv("PY_POWER_ENERGY_BUDGET_MJ", "1000.0"))

    def _load_from_file(self, config_file: Path) -> None:
        """Load configuration from a specific file."""
        try:
            if config_file.name == "pyproject.toml":
                with open(config_file, "rb") as f:
                    data = tomllib.load(f)
                    if "tool" in data and "py-power-profile" in data["tool"]:
                        config = data["tool"]["py-power-profile"]
                        self._update_from_dict(config)
            else:
                with open(config_file, "rb") as f:
                    config = tomllib.load(f)
                    self._update_from_dict(config)
        except Exception as e:
            print(f"Warning: Could not load config from {config_file}: {e}", file=sys.stderr)

    def _update_from_dict(self, config: Dict[str, Any]) -> None:
        """Update configuration from a dictionary."""
        if "backend" in config:
            self.backend = config["backend"]
        if "tdp_watts" in config:
            self.tdp_watts = float(config["tdp_watts"])
        if "energy_budget_mj" in config:
            self.energy_budget_mj = float(config["energy_budget_mj"])
        if "ignore" in config:
            self.ignore_patterns = config["ignore"]

    def should_ignore(self, path: str) -> bool:
        """Check if a path should be ignored based on patterns."""
        import fnmatch

        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
        return False


# Global configuration instance
config = Config() 