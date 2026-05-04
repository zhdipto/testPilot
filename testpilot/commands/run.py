"""run command — execute test suites and stream results."""

from __future__ import annotations

import typer
from pathlib import Path
from rich.console import Console

from testpilot.services.runner_service import RunnerService
from testpilot.utils.console import print_success, print_error, print_info

app = typer.Typer()
console = Console()


@app.command()
def run(
    test_path: Path = typer.Argument(
        Path("tests"),
        help="Path to a test file or directory.",
        exists=False,
        resolve_path=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output for each test.",
    ),
    fail_fast: bool = typer.Option(
        False,
        "--fail-fast",
        "-x",
        help="Stop on first failure.",
    ),
    save_report: bool = typer.Option(
        False,
        "--save-report",
        "-s",
        help="Save a JSON report to [cyan]./reports/[/cyan] after running.",
    ),
) -> None:
    """
    [bold]Run[/bold] tests and display a rich summary table.

    Example:
        [green]testpilot run tests/ --verbose --save-report[/green]
    """
    if not test_path.exists():
        print_error(f"Path not found: [bold]{test_path}[/bold]")
        raise typer.Exit(code=1)

    print_info(f"Running tests in [cyan]{test_path}[/cyan]")

    service = RunnerService(verbose=verbose, fail_fast=fail_fast)
    summary = service.run(test_path=test_path, save_report=save_report)

    if summary["failed"] == 0:
        print_success(
            f"[bold green]{summary['passed']}[/bold green] passed, "
            f"[bold red]{summary['failed']}[/bold red] failed — "
            f"[dim]{summary['duration']:.2f}s[/dim]"
        )
    else:
        print_error(
            f"[bold green]{summary['passed']}[/bold green] passed, "
            f"[bold red]{summary['failed']}[/bold red] failed — "
            f"[dim]{summary['duration']:.2f}s[/dim]"
        )
        raise typer.Exit(code=1)
