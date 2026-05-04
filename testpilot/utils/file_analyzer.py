"""Utility for validating, reading, and previewing source code files."""

from pathlib import Path
import typer
from rich.console import Console
from rich.syntax import Syntax

from testpilot.utils.console import print_error, print_info

console = Console()


def process_source_file(file_path: Path) -> str:
    """
    Validate the file path, check the extension, read the content,
    and display a preview of the first 20 lines.
    
    Returns the full content of the file.
    Exits with code 1 if any validation fails.
    """
    # Validate file path
    if not file_path.exists():
        print_error(f"File not found: [bold]{file_path}[/bold]")
        raise typer.Exit(code=1)
    if not file_path.is_file():
        print_error(f"Path is not a file: [bold]{file_path}[/bold]")
        raise typer.Exit(code=1)

    # Detect extension
    ext = file_path.suffix.lower()
    valid_extensions = {".py", ".js", ".ts"}
    if ext not in valid_extensions:
        print_error(f"Unsupported file extension '{ext}'. Supported: {', '.join(valid_extensions)}")
        raise typer.Exit(code=1)

    # Read code file
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print_error(f"Failed to read file: {e}")
        raise typer.Exit(code=1)

    # Show first 20 lines preview
    print_info(f"Loaded [bold]{file_path.name}[/bold] ({ext})")
    lines = content.splitlines()
    preview_lines = lines[:20]
    preview_text = "\n".join(preview_lines)

    lexer = "python"
    if ext == ".js":
        lexer = "javascript"
    elif ext == ".ts":
        lexer = "typescript"

    syntax = Syntax(preview_text, lexer, line_numbers=True, word_wrap=True)
    console.print(syntax)

    if len(lines) > 20:
        console.print(f"[dim]... and {len(lines) - 20} more lines[/dim]")

    return content
