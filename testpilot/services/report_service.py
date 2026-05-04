"""ReportService — load, display and export JSON test reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class ReportService:
    """Load and render JSON reports produced by RunnerService."""

    REPORTS_DIR = Path("reports")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def latest_report(self) -> Path | None:
        """Return the most recent JSON report file, or None."""
        if not self.REPORTS_DIR.exists():
            return None
        reports = sorted(self.REPORTS_DIR.glob("report_*.json"))
        return reports[-1] if reports else None

    def display(self, report_file: Path) -> None:
        """Render a rich table from a JSON report."""
        data = self._load(report_file)

        # Header panel
        status = "[green]PASSED[/green]" if data.get("failed", 0) == 0 else "[red]FAILED[/red]"
        console.print(
            Panel(
                f"[bold]Status:[/bold] {status}  |  "
                f"[bold]Duration:[/bold] {data.get('duration', 0):.2f}s",
                title=f"[bold cyan]TestPilot Report[/bold cyan] — {report_file.name}",
                border_style="cyan",
            )
        )

        # Summary table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")
        table.add_row("Test Path", str(data.get("test_path", "—")))
        table.add_row("Passed", f"[green]{data.get('passed', 0)}[/green]")
        table.add_row("Failed", f"[red]{data.get('failed', 0)}[/red]")
        table.add_row("Errors", f"[yellow]{data.get('errors', 0)}[/yellow]")
        table.add_row("Duration", f"{data.get('duration', 0):.2f}s")
        table.add_row("Return Code", str(data.get("returncode", "—")))
        console.print(table)

        # Raw output section
        if data.get("output"):
            console.print(
                Panel(
                    data["output"].strip(),
                    title="[dim]Raw pytest output[/dim]",
                    border_style="dim",
                )
            )

    def export_html(self, report_file: Path) -> Path:
        """Write a minimal HTML report next to the JSON file."""
        data = self._load(report_file)
        out = report_file.with_suffix(".html")
        status = "PASSED" if data.get("failed", 0) == 0 else "FAILED"
        color = "#22c55e" if status == "PASSED" else "#ef4444"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>TestPilot Report — {report_file.name}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background:#0f172a; color:#e2e8f0; padding:2rem; }}
    h1 {{ color:#38bdf8; }}
    .badge {{ display:inline-block; padding:.3rem .8rem; border-radius:.4rem;
               background:{color}; color:#fff; font-weight:700; font-size:1.1rem; }}
    table {{ border-collapse:collapse; margin-top:1rem; width:100%; max-width:480px; }}
    th,td {{ padding:.5rem 1rem; border:1px solid #334155; text-align:left; }}
    th {{ background:#1e293b; color:#38bdf8; }}
    pre {{ background:#1e293b; padding:1rem; border-radius:.5rem;
            overflow-x:auto; font-size:.85rem; color:#94a3b8; }}
  </style>
</head>
<body>
  <h1>TestPilot Report</h1>
  <p><span class="badge">{status}</span></p>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Test Path</td><td>{data.get('test_path','—')}</td></tr>
    <tr><td>Passed</td><td style="color:#22c55e">{data.get('passed',0)}</td></tr>
    <tr><td>Failed</td><td style="color:#ef4444">{data.get('failed',0)}</td></tr>
    <tr><td>Errors</td><td style="color:#f59e0b">{data.get('errors',0)}</td></tr>
    <tr><td>Duration</td><td>{data.get('duration',0):.2f}s</td></tr>
  </table>
  <h2>Output</h2>
  <pre>{data.get('output','').strip()}</pre>
</body>
</html>"""

        out.write_text(html, encoding="utf-8")
        return out

    def export_csv(self, report_file: Path) -> Path:
        """Write a CSV summary next to the JSON file."""
        data = self._load(report_file)
        out = report_file.with_suffix(".csv")
        fields = ["test_path", "passed", "failed", "errors", "duration", "returncode"]
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerow({k: data.get(k, "") for k in fields})
        return out

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load(self, report_file: Path) -> dict[str, Any]:
        try:
            return json.loads(report_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise ValueError(f"Cannot load report: {exc}") from exc
