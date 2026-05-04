"""coverage command — AI coverage analysis."""

from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from testpilot.utils.console import print_info, print_error
from testpilot.utils.file_analyzer import process_source_file
from testpilot.services.openai_service import ask_ai

app = typer.Typer()
console = Console()

@app.command()
def coverage(
    file: Path = typer.Argument(..., help="Python file to analyse coverage for."),
) -> None:
    """Analyse test coverage for a Python file using AI."""
    print_info(f"[bold]coverage[/bold] → [cyan]{file}[/cyan]")
    
    content = process_source_file(file)
    
    prompt = f"""
You are an expert QA and Python Test Engineer.
Analyze the following Python code from the file `{file.name}` and suggest a comprehensive test coverage plan.

Your response must be formatted as a **Markdown Checklist** (e.g. using `- [ ]` syntax) and strictly categorized into the following four sections:

1. **Missing Tests**: What basic/core tests need to be written?
2. **Edge Cases Not Covered**: What tricky inputs, boundary conditions, or unusual states should be tested?
3. **Security Tests**: What tests are needed for vulnerabilities, injections, or access controls?
4. **Performance Cases**: What tests should verify speed, memory limits, or large inputs?

Ensure the output uses `- [ ]` syntax for every item so it looks like a clear, actionable checklist. Do not include extra conversational text.

CODE:
{content}
"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("AI is generating coverage checklist...", total=None)
        try:
            analysis = ask_ai(prompt)
        except Exception as e:
            print_error(f"Failed to get AI coverage analysis: {e}")
            raise typer.Exit(code=1)

    console.print()
    console.print(Panel(
        Markdown(analysis),
        title=f"[bold green]Coverage Analysis: {file.name}[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
