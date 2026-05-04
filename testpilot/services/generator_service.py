"""GeneratorService — use AI to generate complete test suites."""

from pathlib import Path
from testpilot.services.openai_service import ask_ai


class GeneratorService:
    """Use OpenAI to generate complete test suites for a Python module."""

    FRAMEWORKS = ("pytest", "unittest")

    def __init__(self, framework: str = "pytest") -> None:
        if framework not in self.FRAMEWORKS:
            raise ValueError(f"Unsupported framework '{framework}'. Choose from {self.FRAMEWORKS}.")
        self.framework = framework

    def generate(
        self,
        source_path: Path,
        output_dir: Path,
        overwrite: bool = False,
    ) -> Path:
        """Read source, ask AI for tests, and write the test file."""
        source = source_path.read_text(encoding="utf-8")

        prompt = f"""
You are an expert Python test engineer.
Write a comprehensive {self.framework} test suite for the following Python code.
The code is from the file `{source_path.name}`.

Ensure the generated tests cover:
- Normal/happy path cases
- Edge cases
- Invalid inputs
- Expected exceptions
- Mocks if external dependencies or I/O are involved
- Async tests if there are async functions

Include all necessary imports and use best practices.
CRITICAL: You MUST import the functions you are testing from the module `{source_path.stem}` (e.g. `from {source_path.stem} import ...`).
Output ONLY the raw Python code. Do NOT wrap the code in markdown blocks (e.g. ```python). Do NOT include any explanations.

CODE:
{source}
"""
        # Call the AI service
        content = ask_ai(prompt).strip()

        # Fallback strip in case AI still adds markdown blocks
        if content.startswith("```python"):
            content = content[9:].strip()
        elif content.startswith("```"):
            content = content[3:].strip()
            
        if content.endswith("```"):
            content = content[:-3].strip()

        # Write the file
        test_file = output_dir / f"test_{source_path.stem}.py"
        if test_file.exists() and not overwrite:
            raise FileExistsError(
                f"{test_file} already exists. Use --overwrite to replace it."
            )

        test_file.write_text(content, encoding="utf-8")
        return test_file
