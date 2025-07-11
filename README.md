# gym-collabsort

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
# The optional -s flag prints code output
uv run pytest [-s]
```

## License

[MIT](LICENSE).

Copyright © 2025-present [Baptiste Pesquet](https://www.bpesquet.fr).
