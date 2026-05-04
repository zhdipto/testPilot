"""Shared Rich console helpers used across all commands."""

from __future__ import annotations

from rich.console import Console

console = Console()


def print_success(message: str) -> None:
    """Print a green ✓ success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    """Print a red ✗ error message."""
    console.print(f"[bold red]✗[/bold red] {message}")


def print_info(message: str) -> None:
    """Print a blue ℹ info message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def print_warning(message: str) -> None:
    """Print a yellow ⚠ warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_banner() -> None:
    """Print the TestPilot ASCII banner."""
    banner = r"""
  _____ ____ ____ _____ ____  _ _       _
 |_   _|  __|  __|_   _|  _ \(_) | ___ | |_
   | | | _|  _|  | | | |_) | | |/ _ \| __|
   | | | |__| |__ | | |  __/| | | (_) | |_
   |_| |____|____||_| |_|   |_|_|\___/ \__|
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    console.print("[dim]Professional Python Test Case Generator[/dim]\n")
