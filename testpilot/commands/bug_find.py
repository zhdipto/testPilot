"""bug-find command — AI bug scanner."""

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
def bug_find(
    file: Path = typer.Argument(..., help="Python file to scan for bugs."),
) -> None:
    """Scan a Python file for potential bugs using AI."""
    print_info(f"[bold]bug-find[/bold] → [cyan]{file}[/cyan]")
    
    content = process_source_file(file)
    
    prompt = f"""
You are an expert Python security and code reviewer.
Analyze the following Python code from the file `{file.name}` and scan it for potential issues.

Look specifically for:
- **Null Issues**: Unhandled None types, missing existence checks.
- **Logic Bugs**: Flaws in the business logic or unexpected behaviors.
- **Race Conditions**: Concurrency, threading, or state issues.
- **Bad Code Smell**: Anti-patterns, unmaintainable code, or messy implementations.
- **Security Issues**: Injections, hardcoded secrets, cryptographic flaws, etc.

Format your response in Markdown. For every issue you find, you MUST assign a severity level using exactly one of these labels: **[HIGH]**, **[MEDIUM]**, or **[LOW]**. 

Structure your response clearly with headings or bullet points. If no issues are found, state clearly that the code looks solid.

CODE:
{content}
"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("AI is hunting for bugs...", total=None)
        try:
            report = ask_ai(prompt)
        except Exception as e:
            print_error(f"Failed to get AI bug report: {e}")
            raise typer.Exit(code=1)

    console.print()
    console.print(Panel(
        Markdown(report),
        title=f"[bold red]Bug Report: {file.name}[/bold red]",
        border_style="red",
        padding=(1, 2)
    ))
