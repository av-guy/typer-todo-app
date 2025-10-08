[![codecov](https://codecov.io/gh/av-guy/typer-todo-app/branch/main/graph/badge.svg)](https://codecov.io/gh/av-guy/typer-todo-app)

# Task Manager CLI

A simple Typer-based command-line app for managing tasks and todos.

## Setup

Clone the repo and enter the directory:

```bash
git clone https://github.com/av-guy/typer-todo-app.git
cd typer-todo-app
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install .           # Core dependencies
pip install .[dev]      # Dev/test tools
```

## Run the App

Use the help command to explore available commands:

```bash
python -m src.task_manager --help
```

## Run Tests

```bash
pytest
```

## Build and Install

Install the build tool:

```bash
python -m pip install --upgrade build
```

Build the package:

```bash
python -m build
```

Install from the generated archive:

```bash
pip install dist/task_manager-0.0.1.tar.gz
```

After installation, run the CLI:

```bash
task-manager --help
```

_If you follow these instructions, this application will only be available from within your virtual environment_

# Installing From GitHub

Without cloning the repository, you can run:

```bash
pip install git+https://github.com/av-guy/typer-todo-app
```

After installation, run the CLI:

```bash
task-manager --help
```
