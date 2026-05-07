"""ManualReportService — converts pytest JSON reports into QA-standard manual test reports."""

from __future__ import annotations

import ast
import datetime
import json
import re
from pathlib import Path
from typing import Any

from rich.console import Console as RichConsole
from rich.panel import Panel
from rich.table import Table


REPORTS_DIR = Path("reports")


# ---------------------------------------------------------------------------
# Classifier helpers
# ---------------------------------------------------------------------------

def _classify_test_type(test_name: str) -> str:
    """Automatically determine test type from function name."""
    name = test_name.lower()
    if any(k in name for k in ("argv", "main_valid", "main_invalid", "cli", "main")):
        return "CLI"
    if any(k in name for k in ("invalid", "bad", "wrong", "corrupt", "mixed")):
        return "Error Handling"
    if any(k in name for k in ("empty", "single", "zero", "none", "null", "boundary")):
        return "Edge Case"
    return "Unit"


def _make_tc_id(index: int) -> str:
    return f"TC_{index:03d}"


def _humanize(test_name: str) -> str:
    """Convert snake_case test function name into a readable title."""
    name = re.sub(r"^test_", "", test_name)
    return name.replace("_", " ").title()


# ---------------------------------------------------------------------------
# pytest output parsers
# ---------------------------------------------------------------------------

def _extract_test_blocks(raw_output: str) -> dict[str, str]:
    """
    Parse pytest --tb=short output and return a dict of
    {test_function_name: failure_block_text} for all failed tests.
    """
    failures: dict[str, str] = {}
    pattern = re.compile(
        r"_{10,}\s+([\w::/.\[\]-]+)\s+_{10,}\n(.*?)(?=_{10,}|\Z)", re.DOTALL
    )
    for match in pattern.finditer(raw_output):
        node_id = match.group(1).strip()
        block = match.group(2).strip()
        func_name = node_id.split("::")[-1]
        failures[func_name] = block
    return failures


def _extract_error_line(failure_block: str) -> str:
    """Pull the most relevant error line from a pytest failure block."""
    for line in failure_block.splitlines():
        stripped = line.strip()
        if stripped.startswith("E "):
            return stripped[2:].strip()
    return failure_block.splitlines()[-1].strip() if failure_block else "Unknown error"


def _read_test_names_from_file(test_path: Path) -> list[str]:
    """
    Parse the test source file with ast and return top-level test function names
    in declaration order. This is reliable regardless of pytest verbosity.
    """
    try:
        tree = ast.parse(test_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return []
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            names.append(node.name)
    return names


def _parse_test_names_and_status(
    raw_output: str,
    passed: int,
    failed: int,
    test_path: Path | None = None,
) -> list[dict[str, Any]]:
    """
    Return an ordered list of {name, status} dicts for every test in the suite.

    Strategy:
      1. Read test function names from the source file via AST (primary — works
         regardless of pytest verbosity level).
      2. Fall back to regex-scanning raw_output when the file is unavailable.
      3. Cross-reference with FAILED summary lines from raw_output to assign
         each test its correct PASS / FAIL status.
    """
    # Collect failed function names from "FAILED path::func" summary lines
    summary_pattern = re.compile(r"FAILED\s+[\w:/\\.\[\]-]+::([\w\[\]-]+)")
    failed_names = {m.group(1) for m in summary_pattern.finditer(raw_output)}

    # Primary: read names from source file
    if test_path and test_path.is_file():
        ordered = _read_test_names_from_file(test_path)
    else:
        # Fallback: scrape names from raw output (only reliable with -v)
        all_mentioned = re.findall(
            r"\btest_[a-z][a-z0-9]*(?:_[a-z][a-z0-9]*)+\b", raw_output
        )
        seen: set[str] = set()
        ordered = []
        for name in all_mentioned:
            if name not in seen:
                seen.add(name)
                ordered.append(name)

    return [
        {"name": name, "status": "FAIL" if name in failed_names else "PASS"}
        for name in ordered
    ]


# ---------------------------------------------------------------------------
# Inference helpers
# ---------------------------------------------------------------------------

def _infer_input(test_name: str) -> str:
    name = test_name.lower()
    if "empty" in name:
        return "[] (empty list / no arguments)"
    if "single" in name:
        return "[5] (single-element list)"
    if "mixed" in name:
        return '["1", "a", "3"] (mixed valid and invalid values)'
    if "invalid" in name and "parse" in name:
        return '["a", "b", "c"] (non-numeric strings)'
    if "invalid_input" in name:
        return "sys.argv = ['app.py', 'a', 'b', 'c'] (non-numeric CLI args)"
    if "invalid_args" in name:
        return "sys.argv = ['app.py'] (no numeric arguments)"
    if "mock" in name and "argv" in name:
        return "sys.argv = ['app.py', '1', '2', '3']"
    if "valid" in name and "parse" in name:
        return '["1", "2", "3"] (valid string integers)'
    if ("valid" in name or "main" in name) and "async" not in name:
        return "sys.argv = ['app.py', '1', '2', '3']"
    if "normal" in name or "average" in name:
        return "[1, 2, 3, 4, 5]"
    if "async" in name:
        return "sys.argv = ['app.py', '1', '2', '3'] (async execution context)"
    return "As defined in test body"


def _infer_expected(test_name: str) -> str:
    name = test_name.lower()
    if "average" in name and "empty" in name:
        return "ZeroDivisionError raised"
    if "average" in name and "single" in name:
        return "Returns 5.0"
    if "average" in name and "normal" in name:
        return "Returns 3.0"
    if "parse" in name and "empty" in name:
        return "Returns []"
    if "parse" in name and ("invalid" in name or "mixed" in name):
        return "ValueError raised"
    if "parse" in name and "valid" in name:
        return "Returns [1, 2, 3]"
    if "main" in name and "invalid_input" in name:
        return "ValueError raised (non-numeric args propagate from parse_input)"
    if "main" in name and "invalid_args" in name:
        return 'Prints "Usage: python app.py <numbers>" to stdout'
    if "main" in name and "valid" in name and "invalid" not in name:
        return 'Prints "Average: 2.00" to stdout'
    if "async" in name:
        return 'Prints "Average: 2.00" in async execution context'
    if "mock" in name:
        return "Returns [1, 2, 3] after parsing mocked sys.argv"
    return "Function executes without error and returns the correct value"


def _build_test_case(
    index: int, entry: dict[str, Any], failure_blocks: dict[str, str]
) -> dict[str, Any]:
    name = entry["name"]
    status = entry["status"]
    test_type = _classify_test_type(name)
    human_name = _humanize(name)

    precondition_map = {
        "CLI": (
            "sys.argv is patched via unittest.mock.patch; "
            "sys.stdout is captured to verify printed output."
        ),
        "Edge Case": (
            "Target function is imported from the source module; "
            "edge-case input is prepared (e.g., empty list, single element)."
        ),
        "Error Handling": (
            "Target function is imported from the source module; "
            "invalid or malformed input is prepared."
        ),
        "Unit": (
            "Target function is imported from the source module; "
            "valid representative input is prepared."
        ),
    }

    steps_map = {
        "Unit": [
            "Import the target function from the source module.",
            "Prepare the valid input data.",
            "Call the function with the prepared input.",
            "Assert the return value matches the expected output.",
        ],
        "Edge Case": [
            "Import the target function from the source module.",
            "Prepare the edge-case input (e.g., empty list, single element).",
            "Call the function with the edge-case input.",
            "Assert the return value or raised exception matches the expected output.",
        ],
        "Error Handling": [
            "Import the target function from the source module.",
            "Prepare invalid or malformed input data.",
            "Call the function within a pytest.raises() context.",
            "Assert that the correct exception type and message are raised.",
        ],
        "CLI": [
            "Patch sys.argv with the target command-line arguments using unittest.mock.patch.",
            "Capture stdout output (via StringIO or MagicMock).",
            "Call the main() function.",
            "Assert that the output matches the expected printed string.",
        ],
    }

    error_msg = ""
    actual_output = "As expected — no deviation observed."
    if status == "FAIL":
        block = failure_blocks.get(name, "")
        error_msg = _extract_error_line(block)
        actual_output = error_msg if error_msg else "Unexpected failure (see raw pytest output)"

    return {
        "id": _make_tc_id(index),
        "name": human_name,
        "type": test_type,
        "description": (
            f"Verify that `{name}` behaves correctly under "
            f"{test_type.lower()} conditions."
        ),
        "preconditions": precondition_map.get(test_type, "No special preconditions required."),
        "steps": steps_map.get(test_type, steps_map["Unit"]),
        "input": _infer_input(name),
        "expected": _infer_expected(name),
        "actual": actual_output,
        "status": status,
        "error_msg": error_msg,
    }


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------

def _render_markdown(test_cases: list[dict[str, Any]], meta: dict[str, Any]) -> str:
    lines: list[str] = []

    lines += [
        "# Manual Test Report",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| **Project**            | TestPilot CLI |",
        f"| **Test File**          | `{meta.get('test_path', 'N/A')}` |",
        f"| **Execution Duration** | {meta.get('duration', 0):.2f}s |",
        f"| **Report Generated**   | {meta.get('generated_at', 'N/A')} |",
        "",
        "---",
        "",
    ]

    for tc in test_cases:
        status_label = "**PASS**" if tc["status"] == "PASS" else "**FAIL**"
        lines += [
            f"## {tc['id']} — {tc['name']}",
            "",
            "| Field | Details |",
            "|-------|---------|",
            f"| **Test Case ID**    | {tc['id']} |",
            f"| **Test Case Name**  | {tc['name']} |",
            f"| **Test Type**       | {tc['type']} |",
            f"| **Description**     | {tc['description']} |",
            f"| **Preconditions**   | {tc['preconditions']} |",
            f"| **Input Data**      | {tc['input']} |",
            f"| **Expected Output** | {tc['expected']} |",
            f"| **Actual Output**   | {tc['actual']} |",
            f"| **Status**          | {status_label} |",
        ]
        if tc["error_msg"]:
            lines.append(f"| **Error Message**   | `{tc['error_msg']}` |")
        lines.append("")

        lines.append("**Test Steps:**")
        for i, step in enumerate(tc["steps"], 1):
            lines.append(f"{i}. {step}")
        lines += ["", "---", ""]

    # Summary
    total = len(test_cases)
    passed = sum(1 for t in test_cases if t["status"] == "PASS")
    failed = total - passed
    rate = (passed / total * 100) if total > 0 else 0.0

    lines += [
        "## Test Execution Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| **Total Test Cases** | {total} |",
        f"| **Passed**           | {passed} |",
        f"| **Failed**           | {failed} |",
        f"| **Success Rate**     | {rate:.1f}% |",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public service class
# ---------------------------------------------------------------------------

class ManualReportService:
    """Convert a JSON test report into a QA-standard manual test report (.md)."""

    REPORTS_DIR = Path("reports")

    # ------------------------------------------------------------------
    # Core builders
    # ------------------------------------------------------------------

    def build_from_json(
        self, report_file: Path
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Parse a saved JSON report and return (test_cases, meta)."""
        raw: dict[str, Any] = json.loads(report_file.read_text(encoding="utf-8"))
        raw_output: str = raw.get("output", "")
        test_path_str: str = raw.get("test_path", "")
        test_path = Path(test_path_str) if test_path_str else None

        failure_blocks = _extract_test_blocks(raw_output)
        entries = _parse_test_names_and_status(
            raw_output,
            raw.get("passed", 0),
            raw.get("failed", 0),
            test_path=test_path,
        )
        test_cases = [
            _build_test_case(i + 1, entry, failure_blocks)
            for i, entry in enumerate(entries)
        ]
        meta = {
            "test_path": test_path_str or "N/A",
            "duration": raw.get("duration", 0),
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return test_cases, meta

    def run_and_build(
        self, test_file: Path
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Run pytest live on *test_file* and return (test_cases, meta)."""
        from testpilot.services.runner_service import RunnerService

        runner = RunnerService(verbose=False, fail_fast=False)
        summary = runner.run(test_path=test_file, save_report=False)

        raw_output: str = summary.get("output", "")
        failure_blocks = _extract_test_blocks(raw_output)
        entries = _parse_test_names_and_status(
            raw_output,
            summary.get("passed", 0),
            summary.get("failed", 0),
            test_path=test_file,
        )
        test_cases = [
            _build_test_case(i + 1, entry, failure_blocks)
            for i, entry in enumerate(entries)
        ]
        meta = {
            "test_path": str(test_file),
            "duration": summary.get("duration", 0),
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return test_cases, meta

    # ------------------------------------------------------------------
    # Output methods
    # ------------------------------------------------------------------

    def display_in_terminal(
        self, test_cases: list[dict[str, Any]], meta: dict[str, Any]
    ) -> None:
        """Render the manual test report as a rich, color-coded terminal view."""
        console = RichConsole()

        total  = len(test_cases)
        passed = sum(1 for t in test_cases if t["status"] == "PASS")
        failed = total - passed
        rate   = (passed / total * 100) if total > 0 else 0.0

        if failed == 0:
            status_str = "[bold green]ALL PASSED[/bold green]"
        else:
            status_str = f"[bold red]{failed} FAILED[/bold red]"

        # Header panel
        console.print(
            Panel(
                f"[bold]Test File:[/bold]  [cyan]{meta.get('test_path', 'N/A')}[/cyan]\n"
                f"[bold]Duration:[/bold]   {meta.get('duration', 0):.2f}s     "
                f"[bold]Generated:[/bold]  {meta.get('generated_at', 'N/A')}     "
                f"[bold]Status:[/bold]  {status_str}",
                title="[bold cyan]TestPilot — Manual Test Report[/bold cyan]",
                border_style="cyan",
                padding=(1, 2),
            )
        )

        # One panel per test case
        for tc in test_cases:
            is_pass   = tc["status"] == "PASS"
            color     = "green" if is_pass else "red"
            badge     = f"[bold {color}]{tc['status']}[/bold {color}]"

            tbl = Table(
                show_header=True,
                header_style="bold magenta",
                border_style=color,
                expand=True,
                padding=(0, 1),
                show_edge=True,
            )
            tbl.add_column("Field",   style="bold",  min_width=20, no_wrap=True)
            tbl.add_column("Details", overflow="fold")

            tbl.add_row("Test Case ID",    tc["id"])
            tbl.add_row("Test Case Name",  tc["name"])
            tbl.add_row("Test Type",       tc["type"])
            tbl.add_row("Description",     tc["description"])
            tbl.add_row("Preconditions",   tc["preconditions"])
            tbl.add_row("Input Data",      tc["input"])
            tbl.add_row("Expected Output", tc["expected"])
            tbl.add_row("Actual Output",   tc["actual"])
            tbl.add_row("Status",          badge)

            if tc.get("error_msg"):
                tbl.add_row(
                    f"[red]Error Message[/red]",
                    f"[red]{tc['error_msg']}[/red]",
                )

            steps_text = "\n".join(
                f"  {i}. {s}" for i, s in enumerate(tc["steps"], 1)
            )
            tbl.add_row("Test Steps", steps_text)

            console.print(
                Panel(
                    tbl,
                    title=f"[bold]{tc['id']} — {tc['name']}[/bold]",
                    border_style=color,
                    padding=(0, 1),
                )
            )

        # Summary table
        if rate == 100.0:
            rate_color = "green"
        elif rate >= 50.0:
            rate_color = "yellow"
        else:
            rate_color = "red"

        summary_tbl = Table(
            title="[bold cyan]Test Execution Summary[/bold cyan]",
            show_header=True,
            header_style="bold cyan",
            border_style="cyan",
            expand=False,
        )
        summary_tbl.add_column("Metric",  style="bold", min_width=22)
        summary_tbl.add_column("Value",   justify="right", min_width=10)
        summary_tbl.add_row("Total Test Cases", str(total))
        summary_tbl.add_row("Passed",   f"[bold green]{passed}[/bold green]")
        summary_tbl.add_row(
            "Failed",
            f"[bold red]{failed}[/bold red]" if failed else "[dim]0[/dim]",
        )
        summary_tbl.add_row(
            "Success Rate",
            f"[bold {rate_color}]{rate:.1f}%[/bold {rate_color}]",
        )
        console.print(summary_tbl)

    def save_markdown(
        self,
        test_cases: list[dict[str, Any]],
        meta: dict[str, Any],
        report_file: Path | None = None,
    ) -> Path:
        """Write a Markdown report to disk and return the output path."""
        md_content = _render_markdown(test_cases, meta)
        stem = report_file.stem if report_file else f"manual_{int(datetime.datetime.now().timestamp())}"
        out_file = self.REPORTS_DIR / f"{stem}_manual.md"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(md_content, encoding="utf-8")
        return out_file

    # ------------------------------------------------------------------
    # Backward-compatible entry point
    # ------------------------------------------------------------------

    def generate(self, report_file: Path) -> Path:
        """Legacy method: parse *report_file* and write a Markdown report."""
        test_cases, meta = self.build_from_json(report_file)
        return self.save_markdown(test_cases, meta, report_file)
