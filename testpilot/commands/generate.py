"""generate command — scaffold test cases from a source file."""

from __future__ import annotations

import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from testpilot.services.generator_service import GeneratorService
from testpilot.utils.console import print_success, print_error, print_info
from testpilot.utils.file_analyzer import process_source_file
from testpilot.utils.config import load_config

app = typer.Typer()
console = Console()


@app.command()
def generate(
    source: Path = typer.Argument(
        ...,
        help="Path to the Python source file to generate tests for.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Directory to write generated test files.",
    ),
    framework: str = typer.Option(
        None,
        "--framework",
        "-f",
        help="Test framework to use.",
        rich_help_panel="Options",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing test files.",
    ),
) -> None:
    """
    [bold]Generate[/bold] test cases from a Python source file.

    Example:
        [green]testpilot generate src/calculator.py -o tests/ -f pytest[/green]
    """
    config = load_config()
    actual_output = output or Path(config["output"])
    actual_framework = framework or config["framework"]

    actual_output.mkdir(parents=True, exist_ok=True)

    print_info(f"Generating [bold]{actual_framework}[/bold] tests for [cyan]{source.name}[/cyan]")
    process_source_file(source)

    service = GeneratorService(framework=actual_framework)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Analysing source file...", total=None)
        try:
            result = service.generate(source_path=source, output_dir=actual_output, overwrite=overwrite)
            progress.update(task, description="Writing test file...")
        except FileExistsError as exc:
            print_error(str(exc))
            raise typer.Exit(code=1) from exc
        except Exception as exc:
            print_error(f"Unexpected error: {exc}")
            raise typer.Exit(code=1) from exc

    print_success(f"Test file written → [bold]{result}[/bold]")
