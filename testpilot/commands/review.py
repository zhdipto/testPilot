"""review command — AI code review."""

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
def review(
    file: Path = typer.Argument(..., help="Python file to review."),
) -> None:
    """Review a Python file like a Senior Engineer using AI."""
    print_info(f"[bold]review[/bold] → [cyan]{file}[/cyan]")
    
    content = process_source_file(file)
    
    prompt = f"""
You are a Principal Python Engineer conducting a strict code review.
Review the following Python code from the file `{file.name}`.

Your review must explicitly include the following 4 sections formatted clearly in Markdown:
1. **Overall Score**: Provide a score out of 10 (e.g. 7/10) with a one-sentence justification.
2. **Maintainability**: Discuss the architecture, modularity, and future-proofing.
3. **Readability**: Evaluate variable names, docstrings, formatting, and simplicity.
4. **Testability**: Explain how easily this code can be unit tested, identifying any tight coupling or missing dependencies.

Use clean, professional language and provide actionable feedback.

CODE:
{content}
"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("AI Senior Engineer is reviewing...", total=None)
        try:
            feedback = ask_ai(prompt)
        except Exception as e:
            print_error(f"Failed to get AI review: {e}")
            raise typer.Exit(code=1)

    console.print()
    console.print(Panel(
        Markdown(feedback),
        title=f"[bold yellow]Code Review: {file.name}[/bold yellow]",
        border_style="yellow",
        padding=(1, 2)
    ))
