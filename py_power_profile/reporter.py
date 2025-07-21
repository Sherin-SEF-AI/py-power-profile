"""Reporting and output generation."""

import json
from typing import Any, Dict, TextIO

from rich.console import Console
from rich.table import Table
from rich.progress import BarColumn
from rich.text import Text


class Reporter:
    """Generate reports and output for energy profiling results."""

    def __init__(self, console: Console = None) -> None:
        self.console = console or Console()

    def print_table(self, results: Dict[str, Any]) -> None:
        """Print a Rich table with energy profiling results."""
        functions = results.get("functions", {})
        summary = results.get("summary", {})
        
        if not functions:
            self.console.print("No functions were profiled.", style="yellow")
            return
        
        # Sort functions by total energy consumption
        sorted_functions = sorted(
            functions.items(),
            key=lambda x: x[1]["total_energy_mj"],
            reverse=True
        )
        
        table = Table(
            title=f"Energy Profile Results (Backend: {results['metadata']['backend']})",
            show_header=True,
            header_style="bold magenta"
        )
        
        table.add_column("Function", style="cyan", no_wrap=True)
        table.add_column("Calls", justify="right", style="green")
        table.add_column("Total Energy (mJ)", justify="right", style="red")
        table.add_column("Avg Energy (mJ)", justify="right", style="yellow")
        table.add_column("Total Time (ms)", justify="right", style="blue")
        table.add_column("Energy %", justify="right", style="magenta")
        
        total_energy = summary.get("total_energy_mj", 0.0)
        
        for func_key, stats in sorted_functions:
            # Truncate long function names
            display_name = func_key
            if len(display_name) > 50:
                display_name = "..." + display_name[-47:]
            
            energy_percent = (stats["total_energy_mj"] / total_energy * 100) if total_energy > 0 else 0
            
            # Create a simple bar representation
            bar_length = 20
            filled_length = int((energy_percent / 100) * bar_length)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            
            table.add_row(
                display_name,
                str(stats["calls"]),
                f"{stats['total_energy_mj']:.1f}",
                f"{stats['avg_energy_mj']:.1f}",
                f"{stats['total_time_ms']:.1f}",
                f"{energy_percent:.1f}% {bar}"
            )
        
        # Add summary row
        table.add_section()
        table.add_row(
            "[bold]TOTAL[/bold]",
            str(sum(f["calls"] for f in functions.values())),
            f"[bold]{total_energy:.1f}[/bold]",
            "-",
            f"{summary.get('total_time_ms', 0):.1f}",
            "100% " + "█" * 20
        )
        
        self.console.print(table)
        
        # Print summary
        self.console.print(f"\n[bold]Summary:[/bold]")
        self.console.print(f"  Total Energy: {total_energy:.1f} mJ")
        self.console.print(f"  Total Time: {summary.get('total_time_ms', 0):.1f} ms")
        self.console.print(f"  Functions Profiled: {summary.get('function_count', 0)}")
        self.console.print(f"  Backend: {results['metadata']['backend']}")

    def write_json(self, results: Dict[str, Any], output_file: TextIO) -> None:
        """Write results to JSON file."""
        json.dump(results, output_file, indent=2)

    def compare_results(self, old_results: Dict[str, Any], new_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two profiling results and return differences."""
        old_functions = old_results.get("functions", {})
        new_functions = new_results.get("functions", {})
        
        comparison = {
            "old_summary": old_results.get("summary", {}),
            "new_summary": new_results.get("summary", {}),
            "changes": {},
            "regressions": [],
            "improvements": []
        }
        
        # Calculate changes for each function
        all_functions = set(old_functions.keys()) | set(new_functions.keys())
        
        for func_key in all_functions:
            old_stats = old_functions.get(func_key, {})
            new_stats = new_functions.get(func_key, {})
            
            old_energy = old_stats.get("total_energy_mj", 0.0)
            new_energy = new_stats.get("total_energy_mj", 0.0)
            
            if old_energy > 0:
                change_percent = ((new_energy - old_energy) / old_energy) * 100
            else:
                change_percent = 0.0 if new_energy == 0 else float('inf')
            
            comparison["changes"][func_key] = {
                "old_energy_mj": old_energy,
                "new_energy_mj": new_energy,
                "change_percent": change_percent,
                "old_calls": old_stats.get("calls", 0),
                "new_calls": new_stats.get("calls", 0),
            }
            
            # Check for regressions (>10% increase) and improvements (>10% decrease)
            if change_percent > 10:
                comparison["regressions"].append(func_key)
            elif change_percent < -10:
                comparison["improvements"].append(func_key)
        
        # Overall change
        old_total = old_results.get("summary", {}).get("total_energy_mj", 0.0)
        new_total = new_results.get("summary", {}).get("total_energy_mj", 0.0)
        
        if old_total > 0:
            total_change_percent = ((new_total - old_total) / old_total) * 100
        else:
            total_change_percent = 0.0
        
        comparison["total_change_percent"] = total_change_percent
        
        return comparison

    def print_comparison(self, comparison: Dict[str, Any]) -> None:
        """Print comparison results."""
        self.console.print("[bold]Energy Profile Comparison[/bold]")
        
        old_total = comparison["old_summary"].get("total_energy_mj", 0.0)
        new_total = comparison["new_summary"].get("total_energy_mj", 0.0)
        total_change = comparison["total_change_percent"]
        
        # Overall summary
        self.console.print(f"\n[bold]Overall Change:[/bold]")
        self.console.print(f"  Old Total: {old_total:.1f} mJ")
        self.console.print(f"  New Total: {new_total:.1f} mJ")
        
        if total_change > 0:
            self.console.print(f"  Change: [red]+{total_change:.1f}%[/red] (regression)")
        elif total_change < 0:
            self.console.print(f"  Change: [green]{total_change:.1f}%[/green] (improvement)")
        else:
            self.console.print(f"  Change: [yellow]{total_change:.1f}%[/yellow] (no change)")
        
        # Regressions
        if comparison["regressions"]:
            self.console.print(f"\n[bold red]Regressions (>10% increase):[/bold red]")
            for func_key in comparison["regressions"]:
                change = comparison["changes"][func_key]
                self.console.print(f"  {func_key}: +{change['change_percent']:.1f}%")
        
        # Improvements
        if comparison["improvements"]:
            self.console.print(f"\n[bold green]Improvements (>10% decrease):[/bold green]")
            for func_key in comparison["improvements"]:
                change = comparison["changes"][func_key]
                self.console.print(f"  {func_key}: {change['change_percent']:.1f}%")
        
        if not comparison["regressions"] and not comparison["improvements"]:
            self.console.print(f"\n[yellow]No significant changes detected.[/yellow]") 