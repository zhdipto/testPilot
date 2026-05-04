"""TestPilot CLI entry point."""

import typer
from rich.console import Console
from rich import print as rprint

from testpilot.commands.generate import generate
from testpilot.commands.run import run
from testpilot.commands.report import report
from testpilot.commands.explain import explain
from testpilot.commands.coverage import coverage
from testpilot.commands.bug_find import bug_find
from testpilot.commands.review import review

console = Console()

app = typer.Typer(
    name="testpilot",
    help="[bold cyan]TestPilot[/bold cyan] — Professional test case generator & runner.",
    rich_markup_mode="rich",
    no_args_is_help=True,
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
)

# Register commands directly so positional arguments are parsed correctly
app.command(name="generate", help="Generate test cases from a Python source file.")(generate)
app.command(name="run",      help="Run test suites and display results.")(run)
app.command(name="report",   help="View and export test reports.")(report)
app.command(name="explain",  help="Explain what a Python file does.")(explain)
app.command(name="coverage", help="Analyse test coverage for a Python file.")(coverage)
app.command(name="bug-find", help="Scan a Python file for potential bugs.")(bug_find)
app.command(name="review",   help="Review a Python file like a Senior Engineer.")(review)


def version_callback(value: bool) -> None:
    from testpilot import __version__
    if value:
        rprint(f"[bold cyan]TestPilot[/bold cyan] version [bold green]{__version__}[/bold green]")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """
    [bold cyan]TestPilot[/bold cyan] — A professional test case generator and runner.

    Use [bold]testpilot --help[/bold] to explore available commands.
    """


if __name__ == "__main__":
    app()
