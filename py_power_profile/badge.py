"""Badge generation for energy profiling results."""

import json
from typing import Dict, Any


class BadgeGenerator:
    """Generate Shields.io-compatible SVG badges for energy consumption."""

    def __init__(self) -> None:
        self.colors = {
            "green": "#4c1",
            "yellow": "#dfb317", 
            "red": "#e05d44",
            "brightgreen": "#4c1",
            "orange": "#fe7d37",
        }

    def generate_badge(self, results: Dict[str, Any], target_mj: float) -> str:
        """Generate an SVG badge for energy consumption."""
        total_energy = results.get("summary", {}).get("total_energy_mj", 0.0)
        
        # Determine color based on target
        if total_energy <= target_mj:
            color = self.colors["green"]
            status = "PASS"
        elif total_energy <= target_mj * 1.25:
            color = self.colors["yellow"]
            status = "WARN"
        else:
            color = self.colors["red"]
            status = "FAIL"
        
        # Generate SVG
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="a">
    <rect width="200" height="20" rx="3" fill="#fff"/>
  </mask>
  <g mask="url(#a)">
    <path fill="#555" d="M0 0h80v20H0z"/>
    <path fill="{color}" d="M80 0h120v20H80z"/>
    <path fill="url(#b)" d="M0 0h200v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="40" y="15" fill="#010101" fill-opacity=".3">Energy</text>
    <text x="40" y="14">Energy</text>
    <text x="140" y="15" fill="#010101" fill-opacity=".3">{total_energy:.0f}mJ</text>
    <text x="140" y="14">{total_energy:.0f}mJ</text>
  </g>
</svg>'''
        
        return svg

    def generate_status_badge(self, results: Dict[str, Any], target_mj: float) -> str:
        """Generate a status badge (PASS/FAIL)."""
        total_energy = results.get("summary", {}).get("total_energy_mj", 0.0)
        
        if total_energy <= target_mj:
            color = self.colors["green"]
            status = "PASS"
        else:
            color = self.colors["red"]
            status = "FAIL"
        
        # Generate SVG
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="120" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="a">
    <rect width="120" height="20" rx="3" fill="#fff"/>
  </mask>
  <g mask="url(#a)">
    <path fill="#555" d="M0 0h60v20H0z"/>
    <path fill="{color}" d="M60 0h60v20H60z"/>
    <path fill="url(#b)" d="M0 0h120v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="30" y="15" fill="#010101" fill-opacity=".3">Energy</text>
    <text x="30" y="14">Energy</text>
    <text x="90" y="15" fill="#010101" fill-opacity=".3">{status}</text>
    <text x="90" y="14">{status}</text>
  </g>
</svg>'''
        
        return svg

    def write_badge(self, results: Dict[str, Any], target_mj: float, output_file: str, status_only: bool = False) -> None:
        """Write badge to file."""
        if status_only:
            svg = self.generate_status_badge(results, target_mj)
        else:
            svg = self.generate_badge(results, target_mj)
        
        with open(output_file, "w") as f:
            f.write(svg) 