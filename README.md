# gym-collabsort

[![Dynamic TOML Badge: Python](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fbpesquet%2Fgym-collabsort%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&query=%24.project.requires-python&label=Python&labelColor=%233776AB&color=black)](pyproject.toml)
[![GitHub Actions workflow status](https://img.shields.io/github/actions/workflow/status/bpesquet/mlcourse/ci.yaml)](https://github.com/bpesquet/gym-collabsort/actions)
[![PyPI Version](https://img.shields.io/pypi/v/gym-collabsort.svg)](https://pypi.org/project/gym-collabsort)

A [Gymnasium](https://gymnasium.farama.org/) environment for training agents on a collaborative sorting task.

## Development notes

### Toolchain

This project is built and tested with the following software:

- [uv](https://docs.astral.sh/uv/) for project management;
- [ruff](https://docs.astral.sh/ruff/) for code formatting and linting;
- [pytest](https://docs.pytest.org) for testing.

### Installation

> [uv](https://docs.astral.sh/uv/) needs to be available on your system.

```bash
git clone https://github.com/bpesquet/gym-collabsort
cd gym-collabsort
uv sync
```

### Useful commands

```bash
# Format all Python files
uvx ruff format

# Lint all Python files and fix any fixable errors
uvx ruff check --fix

# Test the codebase. See pyproject.toml for pytest configuration.
# The optional -s flag prints code output.
# Code coverage reporting is configured in pyproject.toml
uv run pytest [-s]
```

## License

[MIT](LICENSE).

Copyright © 2025-present [Baptiste Pesquet](https://www.bpesquet.fr).
