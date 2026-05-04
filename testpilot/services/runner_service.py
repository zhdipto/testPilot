"""RunnerService — invoke pytest programmatically and capture results."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()


class RunnerService:
    """Run a test suite via pytest subprocess and collect summary data."""

    REPORTS_DIR = Path("reports")

    def __init__(self, verbose: bool = False, fail_fast: bool = False) -> None:
        self.verbose = verbose
        self.fail_fast = fail_fast

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, test_path: Path, save_report: bool = False) -> dict[str, Any]:
        """Execute pytest on *test_path* and return a summary dict."""
        cmd = self._build_command(test_path)

        start = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.perf_counter() - start

        passed, failed, errors = self._parse_output(result.stdout + result.stderr)

        summary: dict[str, Any] = {
            "test_path": str(test_path),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "duration": round(duration, 4),
            "returncode": result.returncode,
            "output": result.stdout,
        }

        self._display_table(summary)

        if save_report:
            self._save_report(summary)

        return summary

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_command(self, test_path: Path) -> list[str]:
        cmd = ["python", "-m", "pytest", str(test_path), "--tb=short", "-q"]
        if self.verbose:
            cmd.append("-v")
        if self.fail_fast:
            cmd.append("-x")
        return cmd

    def _parse_output(self, output: str) -> tuple[int, int, int]:
        """Extract passed/failed/error counts from pytest output."""
        passed = failed = errors = 0
        for line in output.splitlines():
            line = line.strip()
            if "passed" in line:
                for token in line.split(","):
                    token = token.strip()
                    if "passed" in token:
                        try:
                            passed = int(token.split()[0])
                        except (ValueError, IndexError):
                            pass
                    elif "failed" in token:
                        try:
                            failed = int(token.split()[0])
                        except (ValueError, IndexError):
                            pass
                    elif "error" in token:
                        try:
                            errors = int(token.split()[0])
                        except (ValueError, IndexError):
                            pass
        return passed, failed, errors

    def _display_table(self, summary: dict[str, Any]) -> None:
        table = Table(title="Test Run Summary", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")

        status_color = "green" if summary["failed"] == 0 else "red"
        table.add_row("Test Path", str(summary["test_path"]))
        table.add_row("Passed", f"[green]{summary['passed']}[/green]")
        table.add_row("Failed", f"[{status_color}]{summary['failed']}[/{status_color}]")
        table.add_row("Errors", f"[yellow]{summary['errors']}[/yellow]")
        table.add_row("Duration", f"{summary['duration']:.2f}s")

        console.print()
        console.print(table)

    def _save_report(self, summary: dict[str, Any]) -> Path:
        self.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = int(time.time())
        report_file = self.REPORTS_DIR / f"report_{timestamp}.json"
        report_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        console.print(f"[dim]Report saved → {report_file}[/dim]")
        return report_file
