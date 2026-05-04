"""explain command — AI code explanation."""

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
def explain(
    file: Path = typer.Argument(..., help="Python file to explain."),
) -> None:
    """Explain what a Python file does using AI."""
    print_info(f"[bold]explain[/bold] → [cyan]{file}[/cyan]")
    
    # process_source_file prints a preview and returns the file content
    content = process_source_file(file)
    
    prompt = f"""
You are an expert Python developer and code reviewer.
Analyze the following Python code from the file `{file.name}` and provide a detailed explanation.

Your response must include exactly these four sections:
1. **Purpose**: What is the overall goal of this code?
2. **Logic Flow**: How does it work? (Step-by-step or high-level flow)
3. **Possible Bugs**: Are there any edge cases, security issues, or potential bugs?
4. **Testing Strategy**: What approach should be used to test this code effectively?

Use clean, professional Markdown formatting.

CODE:
{content}
"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("AI is analyzing the code...", total=None)
        try:
            explanation = ask_ai(prompt)
        except Exception as e:
            print_error(f"Failed to get AI explanation: {e}")
            raise typer.Exit(code=1)

    # Display the result in a Rich Panel rendering Markdown
    console.print()
    console.print(Panel(
        Markdown(explanation),
        title=f"[bold cyan]Code Explanation: {file.name}[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))
