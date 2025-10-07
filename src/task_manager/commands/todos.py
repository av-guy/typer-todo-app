from typing import Annotated
from enum import Enum
from datetime import datetime

from kink import di
from typer import Typer, Argument, Option, Exit
from rich import print as rich_print
from rich.table import Table

from ..models import Task
from ..protocols import TaskRepository

app = Typer(name="task-manager")


class StatusFilter(str, Enum):
    completed = "completed"
    pending = "pending"
    overdue = "overdue"
    all = "all"


TASK_ID = Annotated[
    int,
    Argument(
        help="The ID of the task.",
        min=1
    )
]

TASK_NAME = Annotated[
    str,
    Argument(help="The name of the task to create.")
]

TASK_DESCRIPTION = Annotated[
    str,
    Option("--description", "-d", help="Optional description for the task.")
]

TASK_COMPLETION = Annotated[
    bool,
    Option("--complete", "-c", help="Whether the task is already complete.")
]

TASK_DUE_DATE = Annotated[
    datetime,
    Argument(help="The due date for the task.")
]

STATUS_FILTER = Annotated[
    StatusFilter,
    Option("--status", "-s",
           help="Filter by task status: completed, pending, or overdue.")
]

UPDATE_NAME = Annotated[
    str,
    Option("--name", "-n", help="New name for the task.")
]

UPDATE_DESCRIPTION = Annotated[
    str,
    Option("--description", "-d", help="New description for the task.")
]

UPDATE_DUE_DATE = Annotated[
    datetime | None,
    Option("--due", help="New due date for the task.")
]

UPDATE_COMPLETION = Annotated[
    bool,
    Option("--complete", "-c", help="Mark the task as complete or incomplete.")
]


@app.command("create")
def create_task(
    name: TASK_NAME,
    due_date: TASK_DUE_DATE,
    description: TASK_DESCRIPTION = "",
    complete: TASK_COMPLETION = False,
):
    """Create a new task."""
    repo: TaskRepository = di[TaskRepository]

    task = Task(
        name=name,
        due_date=due_date,
        description=description,
        completed=complete,
    )

    task_id = repo.add(task)
    rich_print(f"\n[green]Task created with ID {task_id}[/green]\n")


@app.command("list")
def list_tasks(status: STATUS_FILTER = StatusFilter.all):
    """List tasks, optionally filtered by status."""
    repo = di[TaskRepository]

    if status == StatusFilter.completed:
        tasks = repo.filter_by_status(completed=True)
    elif status == StatusFilter.pending:
        tasks = repo.filter_by_status(
            completed=False, due_after=datetime.now())
    elif status == StatusFilter.overdue:
        tasks = repo.filter_by_status(
            completed=False, due_before=datetime.now())
    else:
        tasks = repo.list()

    if not tasks:
        rich_print("\n[yellow]No tasks found[/yellow]\n")
        return

    table = Table(title="Tasks", show_lines=True)
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Name", style="bold white")
    table.add_column("Due Date", style="magenta")
    table.add_column("Description", style="dim")
    table.add_column("Status", style="green")

    for t in tasks:
        status_icon = (
            "✅ Completed" if t.completed
            else "⌛ Pending" if t.due_date >= datetime.now()
            else "❌ Overdue"
        )

        table.add_row(
            str(t.id),
            t.name,
            t.due_date.strftime("%Y-%m-%d"),
            t.description or "-",
            status_icon,
        )

    rich_print("")
    rich_print(table)
    rich_print("")


@app.command("complete")
def complete_task(task_id: TASK_ID):
    """Mark a task as complete."""
    repo: TaskRepository = di[TaskRepository]

    task = repo.get(task_id)
    if not task:
        rich_print(f"\n[red]Task {task_id} not found[/red]\n")
        raise Exit(code=2)

    repo.complete(task_id)
    rich_print(f"\n[green]Task {task_id} marked complete[/green]\n")


@app.command("delete")
def delete_task(task_id: TASK_ID):
    """Delete a task."""
    repo: TaskRepository = di[TaskRepository]

    task = repo.get(task_id)
    if not task:
        rich_print(f"\n[red]Task {task_id} not found[/red]\n")
        raise Exit(code=2)

    repo.delete(task)
    rich_print(f"\n[green]Task {task_id} deleted[/green]\n")


@app.command("update")
def update_task(
    task_id: TASK_ID,
    name: UPDATE_NAME = "",
    description: UPDATE_DESCRIPTION = "",
    due_date: UPDATE_DUE_DATE = None,
    complete: UPDATE_COMPLETION = False,
):
    """Update a task."""
    repo: TaskRepository = di[TaskRepository]

    task = repo.get(task_id)
    if not task:
        rich_print(f"\n[red]Task {task_id} not found[/red]\n")
        raise Exit(code=2)

    if name:
        task.name = name
    if description:
        task.description = description
    if due_date:
        task.due_date = due_date
    if complete:
        task.completed = complete

    rich_print(f"\n[green]Task {task_id} updated[/green]\n")
