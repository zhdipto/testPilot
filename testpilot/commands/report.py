"""report command — display and export test reports."""

from __future__ import annotations

import typer
from pathlib import Path
from rich.console import Console

from testpilot.services.report_service import ReportService
from testpilot.utils.console import print_error, print_info, print_success

app = typer.Typer()
console = Console()


@app.command()
def report(
    report_file: Path = typer.Argument(
        None,
        help="Path to a JSON report file. Defaults to the latest in [cyan]./reports/[/cyan].",
        exists=False,
        resolve_path=True,
    ),
    export_html: bool = typer.Option(
        False,
        "--html",
        help="Export the report as an HTML file.",
    ),
    export_csv: bool = typer.Option(
        False,
        "--csv",
        help="Export the report as a CSV file.",
    ),
) -> None:
    """
    [bold]View[/bold] and export test reports.

    Example:
        [green]testpilot report reports/report_2024.json --html[/green]
    """
    service = ReportService()

    # Resolve report path
    if report_file is None or not report_file.exists():
        report_file = service.latest_report()
        if report_file is None:
            print_error("No reports found. Run [bold]testpilot run --save-report[/bold] first.")
            raise typer.Exit(code=1)

    print_info(f"Loading report: [cyan]{report_file.name}[/cyan]")
    service.display(report_file)

    if export_html:
        out = service.export_html(report_file)
        print_success(f"HTML report saved → [bold]{out}[/bold]")

    if export_csv:
        out = service.export_csv(report_file)
        print_success(f"CSV report saved → [bold]{out}[/bold]")
