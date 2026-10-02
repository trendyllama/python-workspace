

# Tools
- Do not use ripgrep (`rg`)

- Prefer using the tasks in `.vscode/tasks.json` to generated commands
- This project uses Docker
- use `uv run ruff check --output-format=concise` to check for linting errors
- use `uv run pytest` to run tests
- use `uv run ty check --output-format=concise` to check for type errors
- use `uv run ruff format` to format code

# building the project

- `docker build --tag python-test --file Dockerfile .`

# Running the project

- `docker run --name my-python-container --detach --rm python-test`
- `docker exec --tty --interactive my-python-container sh`


# Testing

- Make sure the `test` directory structure mirrors the `src` directory structure. For example, if you have a file `src/data_structures/queue.py`, the corresponding test file should be located at `test/data_structures/test_queue.py`.
- Make sure outputs are adaptable and not hardcoded - for example my `recipies.json` file can be modifed, recipies can be added or removed, so the tests should not assume a fixed number of recipes or specific recipe names.

# Code Style
- Check for any code duplication and suggest abstracting it out

## Python
- Prefer using standard Python libraries and modules over third-party packages unless necessary.



# Architecture
- `pyproject.toml` for dependency, formatter, and lint configuration.
- `README.md` for the project description.
- `src/` for algorithm, data structure, and Codecademy example modules.
- `tests/` for expected behavior and usage patterns.
- `.vscode/tasks.json` for build, test, and lint commands
