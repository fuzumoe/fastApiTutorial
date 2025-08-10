# FastAPI Project Scaffolding

This lesson covers setting up a professional FastAPI project structure with modern Python tooling including type checking, linting, formatting, and dependency management.

## VS Code Configuration Files

### .vscode Directory

The `.vscode` directory contains project-specific settings that apply to everyone who works on the project. These settings ensure consistent development environments across team members.

### settings.json

The `settings.json` file configures VS Code's behavior for your project.

```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "ruff.enable": true,
    "ruff.lint.enable": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll.ruff": "explicit",
        "source.organizeImports.ruff": "explicit"
    },
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.diagnosticMode": "workspace",
    "python.analysis.inlayHints.variableTypes": true,
    "python.analysis.inlayHints.functionReturnTypes": true,
    "python.testing.pytestArgs": ["tests"],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
    "mypy.dmypy": false,
    "mypy.enabled": true,
    "mypy.runUsingActiveInterpreter": true
}
```

#### Key Settings Explained:

1. **Python Path**: Points to your virtual environment
   ```json
   "python.defaultInterpreterPath": ".venv/bin/python"
   ```

2. **Ruff Configuration**: Enables Ruff for linting and formatting
   ```json
   "ruff.enable": true,
   "ruff.lint.enable": true
   ```

3. **Auto-formatting**: Configures actions to happen when you save files
   ```json
   "editor.formatOnSave": true,
   "editor.codeActionsOnSave": {
       "source.fixAll.ruff": "explicit",
       "source.organizeImports.ruff": "explicit"
   }
   ```

4. **Type Checking**: Configures Pylance's type checking mode
   ```json
   "python.analysis.typeCheckingMode": "basic"
   ```

5. **Testing Configuration**: Sets pytest as the default test framework
   ```json
   "python.testing.pytestArgs": ["tests"],
   "python.testing.unittestEnabled": false,
   "python.testing.pytestEnabled": true
   ```

6. **MyPy Settings**: Configures static type checking
   ```json
   "mypy.enabled": true,
   "mypy.runUsingActiveInterpreter": true
   ```

### launch.json

The `launch.json` file configures debugging configurations and launch tasks.

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Ruff Fix",
            "type": "node-terminal",
            "request": "launch",
            "command": "${workspaceFolder}/.venv/bin/ruff check --fix ${workspaceFolder}",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Ruff Format",
            "type": "node-terminal",
            "request": "launch",
            "command": "${workspaceFolder}/.venv/bin/ruff format ${workspaceFolder}",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Pre-commit Run All",
            "type": "node-terminal",
            "request": "launch",
            "command": "pre-commit run --all-files",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "main:app",
                "--reload",
                "--port",
                "8000"
            ],
            "jinja": true,
            "justMyCode": true,
            "env": {
                "MONGO_PORT": "27019",
                "MONGO_HOST": "localhost",
                "MONGO_USER": "root",
                "MONGO_PASSWORD": "example",
                "MONGO_DB": "fastapi_tutorial"
            }
        }
    ]
}
```

#### Key Configurations Explained:

1. **Ruff Fix**: Runs Ruff's linting with auto-fix
2. **Ruff Format**: Runs Ruff's code formatter
3. **Pre-commit Run All**: Executes all pre-commit hooks
4. **FastAPI**: Launches the FastAPI application with debugging support

### extensions.json

The `extensions.json` file recommends VS Code extensions for your project.

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "matangover.mypy",
    "charliermarsh.ruff",
    "ms-azuretools.vscode-docker",
    "redhat.vscode-yaml",
    "mongodb.mongodb-vscode",
    "tamasfe.even-better-toml",
    "njpwerner.autodocstring",
    "streetsidesoftware.code-spell-checker",
    "mhutchie.git-graph",
    "eamodio.gitlens",
    "usernamehw.errorlens"
  ]
}
```

#### Extension Roles:

1. **Python & Pylance**: Core Python language support
   - `ms-python.python` - Base Python extension
   - `ms-python.vscode-pylance` - Python language server with type checking

2. **Code Quality**: Linting, formatting and type checking
   - `matangover.mypy` - MyPy type checking integration
   - `charliermarsh.ruff` - Fast Python linter and formatter

3. **Technology-specific**: Support for related technologies
   - `ms-azuretools.vscode-docker` - Docker integration
   - `redhat.vscode-yaml` - YAML support for configuration files
   - `mongodb.mongodb-vscode` - MongoDB integration
   - `tamasfe.even-better-toml` - TOML support for `pyproject.toml`

4. **Developer Experience**: Productivity enhancements
   - `njpwerner.autodocstring` - Auto-generates Python docstrings
   - `streetsidesoftware.code-spell-checker` - Spell checking
   - `mhutchie.git-graph` - Git repository visualization
   - `eamodio.gitlens` - Git integration
   - `usernamehw.errorlens` - Enhances error display

### Best Practices

1. **Keep settings consistent**: Match your VS Code settings with your CI/CD pipeline configurations
2. **Add descriptive comments**: Add comments to your settings files to explain non-obvious settings
3. **Version control**: Always include these config files in version control
4. **Update regularly**: Keep extensions and their settings updated as new versions are released
5. **Minimize required extensions**: Only include essential extensions to avoid bloat

## References

Here are links to the official documentation for the tools used in this scaffolding, along with their primary purposes:

### Package Management
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
  - **Purpose**: Provides significantly faster package installation than pip
  - **Benefits**: Lockfile support, improved dependency resolution, virtual environment management
  - **Usage**: `uv add <package>`, `uv venv`, `uv pip compile`

- [pyproject.toml](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/) - Project metadata specification
  - **Purpose**: Central configuration file for modern Python projects
  - **Benefits**: Single source of truth for dependencies, build settings, and tool configurations
  - **Usage**: Defines project metadata, dependencies, and tool-specific settings

### Code Quality & Testing
- [Ruff](https://docs.astral.sh/ruff/) - Fast Python linter and formatter
  - **Purpose**: Ensures code follows style guidelines and catches common errors
  - **Benefits**: 10-100x faster than alternatives (flake8, black), combines linting and formatting
  - **Usage**: Configured in `ruff.toml` or `pyproject.toml`

- [mypy](https://mypy.readthedocs.io/) - Static type checker for Python
  - **Purpose**: Performs type checking based on Python type annotations
  - **Benefits**: Catches type-related errors before runtime, improves code clarity
  - **Usage**: Configured in `mypy.ini`, runs as part of pre-commit or manually

- [pytest](https://docs.pytest.org/) - Testing framework
  - **Purpose**: Framework for writing and executing tests
  - **Benefits**: Easy test discovery, extensive plugin ecosystem, powerful fixtures
  - **Usage**: Configured in `pytest.ini`, runs with `python -m pytest`

### Development Workflow
- [pre-commit](https://pre-commit.com/) - Framework for managing git pre-commit hooks
  - **Purpose**: Automates code quality checks before commits
  - **Benefits**: Ensures all committed code meets quality standards, prevents bad commits
  - **Usage**: Configured in `.pre-commit-config.yaml`, activated with `pre-commit install`

- [VS Code settings](https://code.visualstudio.com/docs/getstarted/settings) - Editor configuration
  - **Purpose**: Configures VS Code for optimal Python development
  - **Benefits**: Consistent editor settings across team, integrated linting and formatting
  - **Usage**: Stored in `.vscode/settings.json`, applies automatically in workspace

### FastAPI
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
  - **Purpose**: Framework for building APIs with Python
  - **Benefits**: Automatic OpenAPI docs, type checking, high performance
  - **Usage**: Core library for this tutorial

- [Uvicorn](https://www.uvicorn.org/) - ASGI server implementation
  - **Purpose**: Server that runs FastAPI applications
  - **Benefits**: Fast, standards-compliant ASGI server
  - **Usage**: `uvicorn main:app --reload`

## Prerequisites

- Python 3.12+
- uv (fast Python package manager)
- VS Code (recommended)
- Git (for version control)

## Project Structure

Here's the structure we'll create:

```
fastApiTutorial/
├── .vscode/                # VS Code configuration
│   └── settings.json       # Editor settings
├── .git/                   # Git repository
├── main.py                 # Main application
├── mypy.ini                # Type checking configuration
├── pyproject.toml          # Project metadata and tool configuration
├── pytest.ini              # Testing configuration
├── README.md               # Project documentation
└── ruff.toml               # Linting and formatting configuration
```

## Step 1: Install uv

First, install the uv package manager:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Step 2: Initialize the Project

Create the project directory and initialize with uv:

```bash
mkdir fastApiTutorial
cd fastApiTutorial
uv init
```

## Step 3: Create Virtual Environment with Python 3.12

Set up your Python environment:

```bash
uv venv --python=3.12
```

To activate the environment:
```bash
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

## Step 4: Create the Basic Application

Create `main.py`:

```python
def main() -> None:
    print("Hello from fastapitutorial!")
    return None


if __name__ == "__main__":
    main()
```

## Step 5: Install Dependencies

Install the required packages:

```bash
# Core dependencies
uv add fastapi uvicorn

# Development dependencies
uv add --dev pytest mypy ruff pre-commit
```

## Step 6: Set Up Project Configuration Files

### pyproject.toml

The `pyproject.toml` file is a centralized configuration for modern Python projects:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "fastApiTutorial"
version = "0.1.0"
description = "A tutorial for learning FastAPI"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [
    { name = "Your Name", email = "your.email@example.com" },
]
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "mypy>=1.5.0",
    "ruff>=0.1.0",
]

[tool.ruff]
target-version = "py312"
line-length = 88
select = ["E", "F", "I"]

[tool.mypy]
python_version = "3.12"
strict = true
```

### ruff.toml

Ruff is a fast Python linter and formatter. Create `ruff.toml`:

```toml
# Enable flake8-bugbear (`B`) rules.
select = ["E", "F", "B", "I"]

# Exclude a variety of commonly ignored directories.
exclude = [
    ".bzr",
    ".direnv",
    ".eggs",
    ".git",
    ".git-rewrite",
    ".hg",
    ".mypy_cache",
    ".nox",
    ".pants.d",
    ".pytype",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    "__pypackages__",
    "_build",
    "buck-out",
    "build",
    "dist",
    "node_modules",
    "venv",
]

# Same as Black.
line-length = 88

# Allow unused variables when underscore-prefixed.
dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"

# Target Python 3.12
target-version = "py312"

[format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
```

### mypy.ini

Configure mypy for type checking with `mypy.ini`:

```ini
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True

[mypy.plugins.pydantic1]
enabled = True
```

### pytest.ini

Configure pytest with `pytest.ini`. This file controls the behavior of pytest, our testing framework:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
```

The configuration:
- **testpaths**: Specifies the directories where pytest should look for tests (the `tests` folder)
- **python_files**: Pattern for test files (must start with `test_`)
- **python_functions**: Pattern for test functions (must start with `test_`)
- **python_classes**: Pattern for test classes (must start with `Test`)

This helps organize tests consistently and ensures pytest can automatically discover and run them.

Create a basic test file at `tests/test_main.py`:

```python
from main import main

def test_main_returns_none():
    """Test that the main function returns None."""
    result = main()
    assert result is None

def test_main_runs_without_error():
    """Test that the main function runs without raising exceptions."""
    try:
        main()
        assert True  # If we get here, no exception was raised
    except Exception as e:
        assert False, f"main() raised an exception: {e}"
```

## Step 7: Configure VS Code

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "ruff.enable": true,
    "ruff.lint.enable": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll.ruff": "explicit",
        "source.organizeImports.ruff": "explicit"
    },
    "files.associations": {
        "*.py": "python"
    },
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.tabSize": 4,
        "editor.insertSpaces": true,
        "editor.rulers": [88]
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".ruff_cache": true,
        ".pytest_cache": true
    },
    "search.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".ruff_cache": true,
        ".pytest_cache": true,
        "uv.lock": true
    },
    "python.testing.pytestArgs": ["tests"],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
    "mypy.dmypy": false,
    "mypy.enabled": true,
    "mypy.runUsingActiveInterpreter": true
}
```

## Step 8: Set Up Pre-commit Hooks

Create `.pre-commit-config.yaml` for automated checks before commits:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-json
      - id: mixed-line-ending

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix, --config, /dev/null]
      - id: ruff-format
        args: [--config, /dev/null]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-jinja2]
        args: [--ignore-missing-imports]
```

Initialize pre-commit:

```bash
pre-commit install
```

## Step 9: Create a README

Create `README.md`:

```markdown
# FastAPI Tutorial

This repository contains a step-by-step tutorial for building applications with FastAPI.

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv add fastapi uvicorn
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

- `main.py`: Main application entry point
- `tests/`: Contains pytest test files

## Development Tools

This project uses:
- **uv**: Fast dependency management
- **ruff**: For linting and formatting
- **mypy**: For type checking
- **pre-commit**: For git hooks

## License

MIT
```

## Benefits of This Scaffolding

This scaffolding provides several advantages:

1. **Type Safety**: With mypy, you catch type errors before runtime
2. **Code Quality**: Ruff helps maintain consistent, clean code
3. **Fast Development**: VS Code settings for quick feedback
4. **Dependency Management**: uv for faster package installs and dependency resolution
5. **Git Workflow**: Pre-commit hooks ensure quality checks before commits

## Next Steps

With this scaffolding in place, we'll build on it in the next lesson where we'll create our first FastAPI "Hello World" application.
