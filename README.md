# py-power-profile

Profile and visualize energy consumption of Python code on laptops, desktops, and Raspberry Pi-class devices—no external services or paid APIs required.

## Features

- **Energy Profiling**: Measure energy consumption at function and line level
- **Multiple Backends**: Intel/AMD RAPL, ARM hwmon sensors, and CPU estimation
- **Rich Output**: Beautiful tables with energy breakdowns and visual bars
- **Comparison**: Diff two runs to highlight regressions and improvements
- **Badge Generation**: Create Shields.io-compatible SVG badges for CI/CD
- **GitHub Actions**: Ready-to-use composite action for automated energy testing

## Installation

```bash
pip install py-power-profile
```

For RAPL support (Intel/AMD processors):
```bash
pip install py-power-profile[rapl]
```

## Quick Start

Profile a Python script:
```bash
py-power profile samples/quick.py --output results.json
```

Compare two runs:
```bash
py-power compare old.json new.json
```

Generate a badge:
```bash
py-power badge results.json --target 80
```

## Usage

### Profile Command

```bash
py-power profile <script.py> [--output results.json] [--backend auto] [--line]
```

Options:
- `--output, -o`: Save results to JSON file
- `--backend, -b`: Energy measurement backend (auto, rapl, hwmon, psutil_est, mock)
- `--line`: Enable line-level profiling (coarser accuracy)
- `--quiet, -q`: Suppress output

### Compare Command

```bash
py-power compare old.json new.json
```

Compares two profiling results and highlights:
- Functions with >10% energy increase (regressions)
- Functions with >10% energy decrease (improvements)
- Overall energy change percentage

### Badge Command

```bash
py-power badge results.json --target 80 [--output badge.svg] [--status-only]
```

Options:
- `--target, -t`: Target energy in mJ (default: 80)
- `--output, -o`: Output SVG file (default: stdout)
- `--status-only`: Generate status-only badge (PASS/FAIL)

## Backends

### Auto (Default)
Automatically selects the best available backend:
1. RAPL (Intel/AMD processors)
2. HWMON (ARM/Raspberry Pi)
3. PSUTIL estimation (fallback)

### RAPL
Uses Intel/AMD RAPL (Running Average Power Limit) MSRs for accurate energy measurement.
Requires: `pip install py-power-profile[rapl]`

### HWMON
Reads power sensors from `/sys/class/hwmon` (common on ARM devices).
Available on: Raspberry Pi, ARM-based systems

### PSUTIL Estimation
Estimates energy using CPU usage percentage × TDP × time.
Available on: All systems (fallback)

### Mock
Returns deterministic values for testing.
Available on: All systems

## Configuration

Create `pyproject.toml` or `.pypowerprofile`:

```toml
[tool.py-power-profile]
backend = "auto"
tdp_watts = 15          # CPU TDP for estimation
energy_budget_mj = 1000 # CI threshold
ignore = ["tests/*"]    # glob patterns
```

Environment variables:
- `PY_POWER_BACKEND`: Override backend
- `PY_POWER_TDP_WATTS`: Override TDP
- `PY_POWER_ENERGY_BUDGET_MJ`: Override budget

## GitHub Actions

```yaml
- name: Energy Profile
  uses: your-username/py-power-profile@v1
  with:
    script: samples/quick.py
    output: results.json
    target: 80
```

## Badge Usage

Add to your README:
```markdown
![Energy](https://img.shields.io/endpoint?url=<raw-github-file-url>)
```

## Development

```bash
git clone <repository>
cd py-power-profile
pip install -e .[dev]
pytest
```

## License

MIT License - see LICENSE file for details. 