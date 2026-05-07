"""manual-report command — run tests or load a report and display QA output in terminal."""

from __future__ import annotations

import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from testpilot.services.manual_report_service import ManualReportService
from testpilot.services.report_service import ReportService
from testpilot.utils.console import print_error, print_info, print_success, print_warning

app = typer.Typer()
console = Console()


@app.command()
def manual_report(
    source: Path = typer.Argument(
        None,
        help=(
            "A [bold].py[/bold] test file to run live, "
            "a [bold].json[/bold] saved report to load, "
            "or omit to use the latest saved report automatically."
        ),
        exists=False,
        resolve_path=True,
    ),
    save: bool = typer.Option(
        False,
        "--save",
        "-s",
        help="Also save the report as a [cyan].md[/cyan] file in [cyan]./reports/[/cyan].",
    ),
) -> None:
    """
    [bold]Display[/bold] a QA-standard Manual Test Report in the terminal.

    Examples:
        [green]testpilot manual-report tests/test_foo.py[/green]           (run file live)
        [green]testpilot manual-report reports/report_xyz.json[/green]     (load saved JSON)
        [green]testpilot manual-report[/green]                             (use latest report)
        [green]testpilot manual-report tests/test_foo.py --save[/green]    (run + save .md too)
    """
    service = ManualReportService()
    report_file: Path | None = None

    # ── Route by input type ──────────────────────────────────────────────────
    if source is not None and source.suffix == ".py":
        if not source.exists():
            print_error(f"Test file not found: [bold]{source}[/bold]")
            raise typer.Exit(code=1)

        print_info(f"Running tests in [cyan]{source.name}[/cyan] ...")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Executing test suite...", total=None)
            try:
                test_cases, meta = service.run_and_build(source)
                progress.update(task, description="Building report...")
            except Exception as exc:
                print_error(f"Test run failed: {exc}")
                raise typer.Exit(code=1) from exc

    else:
        # Resolve JSON path ─ given or latest
        if source is not None and source.suffix == ".json" and source.exists():
            report_file = source
        else:
            if source is not None:
                print_warning(
                    f"Could not resolve [bold]{source}[/bold]. "
                    "Falling back to the latest saved report."
                )
            svc = ReportService()
            report_file = svc.latest_report()
            if report_file is None:
                print_error(
                    "No reports found. Pass a [bold].py[/bold] test file directly, "
                    "or run [bold]testpilot run --save-report[/bold] first."
                )
                raise typer.Exit(code=1)

        print_info(f"Loading report: [cyan]{report_file.name}[/cyan]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Parsing test results...", total=None)
            try:
                test_cases, meta = service.build_from_json(report_file)
                progress.update(task, description="Building report...")
            except Exception as exc:
                print_error(f"Failed to parse report: {exc}")
                raise typer.Exit(code=1) from exc

    # ── Display in terminal ──────────────────────────────────────────────────
    service.display_in_terminal(test_cases, meta)

    # ── Optionally save .md ──────────────────────────────────────────────────
    if save:
        try:
            out_file = service.save_markdown(test_cases, meta, report_file)
            print_success(f"Report also saved → [bold]{out_file}[/bold]")
        except Exception as exc:
            print_error(f"Could not save markdown: {exc}")
