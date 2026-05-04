# TestPilot

> **Professional AI-powered Python test case generator and code analysis CLI — powered by Typer, Rich, and OpenAI.**

---

## Features

| Feature | Description |
|---|---|
| **`generate`** | Sends your code to AI to generate a comprehensive `pytest` or `unittest` suite (covering edge cases, mocks, exceptions). |
| **`explain`** | AI breaks down any Python file into Purpose, Logic Flow, Possible Bugs, and Testing Strategy. |
| **`coverage`** | AI scans your code and returns a markdown checklist of missing tests, edge cases, security, and performance tests. |
| **`bug-find`** | AI security & code review hunting for null issues, logic bugs, race conditions, and bad code smells (with HIGH/MEDIUM/LOW severity). |
| **`review`** | AI acts as a Senior Engineer providing a score out of 10, maintainability, readability, and testability feedback. |
| **`run`** | Runs test suites through `pytest` and displays a rich summary table. |
| **`report`** | Loads JSON test reports and exports them as beautiful dark-mode HTML pages or CSV. |

---

## Requirements & Setup

- Python 3.10+
- Virtual environment (already created as `env/`)
- An OpenAI API Key

### 1. Installation

```bash
# 1. Activate the virtual environment
source env/bin/activate          # Linux / macOS
# env\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install TestPilot as an editable CLI tool
pip install -e .
```

### 2. Configure OpenAI API Key
Create a `.env` file in the root of your project:
```env
OPENAI_API_KEY="sk-your-openai-api-key-here"
```

### 3. Global Configuration (Optional)
TestPilot automatically looks for a `testpilot.toml` file in your directory to load defaults.
```toml
# testpilot.toml
framework = "pytest"
model = "gpt-4o"
output = "tests/"
```

---

## Usage Guide

### AI Commands

**Explain code:**
```bash
testpilot explain src/auth.py
```

**Generate test coverage checklist:**
```bash
testpilot coverage src/auth.py
```

**Find bugs and security flaws:**
```bash
testpilot bug-find src/auth.py
```

**Get a Senior Engineer code review:**
```bash
testpilot review src/auth.py
```

**Generate full test cases:**
```bash
# Automatically reads `testpilot.toml` defaults, sends code to AI, and saves to tests/
testpilot generate src/auth.py

# Override config defaults manually
testpilot generate src/auth.py --framework unittest --output custom_tests/ --overwrite
```

### Running Tests & Reports

**Run test suites:**
```bash
# Run all tests in the tests/ directory
testpilot run tests/

# Verbose output, stop on first failure, and save a report
testpilot run tests/ --verbose --fail-fast --save-report
```

**View & export reports:**
```bash
# Display the latest report in a Rich terminal panel
testpilot report

# Export to a dark-mode HTML page and a CSV file
testpilot report --html --csv
```

---

## Project Structure

```
testCaseGenerator/
├── env/                          # Virtual environment
├── testpilot/
│   ├── __init__.py
│   ├── main.py                   # CLI entry point (Typer app)
│   ├── commands/
│   │   ├── generate.py           # testpilot generate
│   │   ├── explain.py            # testpilot explain
│   │   ├── coverage.py           # testpilot coverage
│   │   ├── bug_find.py           # testpilot bug-find
│   │   ├── review.py             # testpilot review
│   │   ├── run.py                # testpilot run
│   │   └── report.py             # testpilot report
│   ├── services/
│   │   ├── openai_service.py     # OpenAI API client
│   │   ├── generator_service.py  # Prompt generation logic
│   │   ├── runner_service.py     # pytest subprocess runner
│   │   └── report_service.py     # JSON report loader & exporter
│   └── utils/
│       ├── config.py             # testpilot.toml loader
│       ├── console.py            # Rich print helpers
│       └── file_analyzer.py      # Path validation, preview & Syntax highlighting
├── examples/                     # Bundled examples to test CLI
├── testpilot.toml                # CLI config
├── .env                          # API keys
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Example Daily Workflow

```bash
# 1. You write a new module
# src/payment.py

# 2. Get a quick AI code review
testpilot review src/payment.py

# 3. Generate the test suite
testpilot generate src/payment.py -o tests/

# 4. Run the generated tests and save the results
testpilot run tests/ --save-report

# 5. Export a beautiful HTML report for the team
testpilot report --html
```

---

## License

MIT
