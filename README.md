# Task Manager

A Typer application for managing your list of todos.

## Setup

Clone the repository:

```bash
git clone https://github.com/av-guy/typer-todo-app.git 
cd typer-todo-app 
```

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv venv  
source venv/bin/activate   # On Windows use: venv\Scripts\activate  
pip install -r requirements.txt
```

## Running the Application

Start the FastAPI app with Uvicorn:

```bash
python -m task_manager todos --help
```

This command will list the available commands for the todos application.

## Running Tests

After creating the virtual environment, run

```bash
pytest
```