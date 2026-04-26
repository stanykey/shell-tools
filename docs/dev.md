# Developer Guide

## Requirements

- Python 3.14+
- `uv` (recommended) or a compatible virtual environment workflow

## Setup

```powershell
uv sync --group dev
```

## Run Commands Locally

Examples:

```powershell
uv run generate-file .\tmp.bin --size 1mb
uv run find-empty-dirs .\tests --no-remove
uv run sync-repos . --recursive
uv run pretty-date
```

`sync-repos` includes `root-dir` itself when it is a git repository; without `--recursive`, it scans only `root-dir` and its direct children.

## Quality Checks

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy shell_tools tests
uv run pre-commit run --all-files
```

## Tests

```powershell
uv run python -m unittest discover -s tests -p "*.py"
```

## Project Structure

- `shell_tools/cli.py`: click command entry points.
- `shell_tools/dirs/`: empty-directory discovery helpers.
- `shell_tools/files/`: random file generation helpers.
- `shell_tools/git/`: git repository discovery/update helpers.
- `tests/`: unit tests by domain (`dirs`, `files`).
