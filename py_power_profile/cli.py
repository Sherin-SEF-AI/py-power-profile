"""Command-line interface for py-power-profile."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .backends import MockBackend
from .badge import BadgeGenerator
from .config import config
from .reporter import Reporter
from .tracer import EnergyTracer
from .utils import get_backend, load_results, save_results, run_script

app = typer.Typer(
    name="py-power",
    help="Profile and visualize energy consumption of Python code",
    add_completion=False,
)
console = Console()


@app.command()
def profile(
    script: str = typer.Argument(..., help="Python script to profile"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output JSON file"),
    backend: str = typer.Option("auto", "--backend", "-b", help="Energy measurement backend"),
    line: bool = typer.Option(False, "--line", help="Enable line-level profiling"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
) -> None:
    """Profile energy consumption of a Python script."""
    try:
        # Validate script file
        script_path = Path(script)
        if not script_path.exists():
            console.print(f"[red]Error: Script file not found: {script}[/red]")
            raise typer.Exit(1)
        
        if not script_path.suffix == ".py":
            console.print(f"[red]Error: File must be a Python script (.py): {script}[/red]")
            raise typer.Exit(1)
        
        # Get backend
        try:
            energy_backend = get_backend(backend)
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
        
        if not energy_backend.is_available():
            console.print(f"[red]Error: Backend '{backend}' is not available on this system[/red]")
            raise typer.Exit(1)
        
        # Create tracer
        tracer = EnergyTracer(energy_backend, line_level=line)
        
        if not quiet:
            console.print(f"[green]Profiling {script} with {energy_backend.get_name()} backend...[/green]")
        
        # Start tracing and run script
        tracer.start()
        try:
            run_script(str(script_path))
        except Exception as e:
            console.print(f"[red]Error running script: {e}[/red]")
            raise typer.Exit(1)
        finally:
            tracer.stop()
        
        # Get results
        results = tracer.get_results()
        
        # Print results
        if not quiet:
            reporter = Reporter(console)
            reporter.print_table(results)
        
        # Save to file if requested
        if output:
            save_results(results, output)
            if not quiet:
                console.print(f"[green]Results saved to: {output}[/green]")
        
        # Exit with error if energy budget exceeded
        total_energy = results.get("summary", {}).get("total_energy_mj", 0.0)
        if total_energy > config.energy_budget_mj:
            if not quiet:
                console.print(f"[red]Energy budget exceeded: {total_energy:.1f} mJ > {config.energy_budget_mj} mJ[/red]")
            raise typer.Exit(1)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Profiling interrupted[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def compare(
    old_file: str = typer.Argument(..., help="Old results JSON file"),
    new_file: str = typer.Argument(..., help="New results JSON file"),
) -> None:
    """Compare two profiling results."""
    try:
        # Load results
        try:
            old_results = load_results(old_file)
            new_results = load_results(new_file)
        except (FileNotFoundError, ValueError) as e:
            console.print(f"[red]Error loading results: {e}[/red]")
            raise typer.Exit(1)
        
        # Compare results
        reporter = Reporter(console)
        comparison = reporter.compare_results(old_results, new_results)
        reporter.print_comparison(comparison)
        
        # Exit with error if there are regressions
        if comparison["regressions"]:
            raise typer.Exit(1)
    
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def badge(
    results_file: str = typer.Argument(..., help="Results JSON file"),
    target: float = typer.Option(80.0, "--target", "-t", help="Target energy in mJ"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output SVG file"),
    status_only: bool = typer.Option(False, "--status-only", help="Generate status-only badge"),
) -> None:
    """Generate an energy consumption badge."""
    try:
        # Load results
        try:
            results = load_results(results_file)
        except (FileNotFoundError, ValueError) as e:
            console.print(f"[red]Error loading results: {e}[/red]")
            raise typer.Exit(1)
        
        # Generate badge
        generator = BadgeGenerator()
        
        if output:
            generator.write_badge(results, target, output, status_only)
            console.print(f"[green]Badge saved to: {output}[/green]")
        else:
            # Print badge to stdout
            if status_only:
                svg = generator.generate_status_badge(results, target)
            else:
                svg = generator.generate_badge(results, target)
            console.print(svg)
        
        # Exit with error if target exceeded
        total_energy = results.get("summary", {}).get("total_energy_mj", 0.0)
        if total_energy > target:
            raise typer.Exit(1)
    
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__
    console.print(f"py-power-profile version {__version__}")


if __name__ == "__main__":
    app() 