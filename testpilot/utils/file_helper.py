"""File system utility helpers."""

from __future__ import annotations

from pathlib import Path


def ensure_dir(path: Path) -> Path:
    """Create *path* (and parents) if it does not exist. Returns the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_stem(path: Path) -> str:
    """Return the file stem without extension, normalised to snake_case."""
    return path.stem.replace("-", "_").replace(" ", "_").lower()


def collect_python_files(directory: Path) -> list[Path]:
    """Recursively collect all *.py files under *directory*."""
    if not directory.is_dir():
        raise NotADirectoryError(f"'{directory}' is not a directory.")
    return sorted(directory.rglob("*.py"))


def read_utf8(path: Path) -> str:
    """Read a file with UTF-8 encoding, raising a clear error on failure."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise OSError(f"Cannot read '{path}': {exc}") from exc


def write_utf8(path: Path, content: str) -> None:
    """Write *content* to *path* with UTF-8 encoding."""
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise OSError(f"Cannot write '{path}': {exc}") from exc
