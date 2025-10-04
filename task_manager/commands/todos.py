from typing import Annotated, Optional, Callable
from contextlib import AbstractContextManager
from enum import Enum
from datetime import datetime

from kink import di
from typer import Typer, Argument, Option
from rich import print as rich_print
from rich.table import Table
from sqlalchemy.orm import sessionmaker, Session

from ..models import Task

app = Typer()


class StatusFilter(str, Enum):
    completed = "completed"
    pending = "pending"
    overdue = "overdue"


TASK_ID = Annotated[
    int,
    Argument(
        help="The ID of the task."
    )
]

TASK_NAME = Annotated[
    str,
    Argument(
        help="The name of the task to create."
    )
]

TASK_DESCRIPTION = Annotated[
    str,
    Option(
        "--description",
        "-d",
        help="An optional description to accompany the task name."
    )
]

TASK_COMPLETION = Annotated[
    bool,
    Option(
        "--complete",
        "-c",
        help="Whether the task is already complete."
    )
]

TASK_DUE_DATE = Annotated[
    datetime,
    Argument(
        help="The due date for the task."
    )
]


STATUS_FILTER = Annotated[
    Optional[StatusFilter],
    Option(
        "--status",
        "-s",
        help="Filter by status: completed, in-progress, or overdue."
    )
]


@app.command("create")
def create_task(
    name: TASK_NAME,
    due_date: TASK_DUE_DATE,
    description: TASK_DESCRIPTION = None,
    complete: TASK_COMPLETION = False,
):
    """Create a new task."""
    db_session: Callable[[],
                         AbstractContextManager[Session]] = di["db_session_context"]

    with db_session() as db:
        if isinstance(db, Session):
            task = Task(name=name, due_date=due_date,
                        description=description, completed=complete)

            db.add(task)
            db.commit()

            rich_print(f"[green]Task created with ID {task.id}[/green]")


@app.command("list")
def list_tasks(status: STATUS_FILTER = None):
    """List tasks, optionally filtered by status."""
    db_session: Callable[[],
                         AbstractContextManager[Session]] = di["db_session_context"]

    with db_session() as db:
        if isinstance(db, Session):
            query = db.query(Task)

            if status == StatusFilter.completed:
                query = query.filter(Task.completed.is_(True))

            elif status == StatusFilter.pending:
                query = query.filter(Task.completed.is_(
                    False), Task.due_date >= datetime.now())

            elif status == StatusFilter.overdue:
                query = query.filter(Task.completed.is_(
                    False), Task.due_date < datetime.now())

            tasks = query.all()

            if not tasks:
                rich_print("[yellow]No tasks found[/yellow]")
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

        rich_print(table)


@app.command("complete")
def complete_task(task_id: TASK_ID):
    """Mark a task as complete."""
    db_session: Callable[[],
                         AbstractContextManager[Session]] = di["db_session_context"]

    with db_session() as db:
        if isinstance(db, Session):
            task = db.get(Task, task_id)

            if not task:
                rich_print(f"[red]Task {task_id} not found[/red]")
                return

            task.completed = True
            db.commit()
            rich_print(f"[green]Task {task_id} marked complete[/green]")


@app.command("delete")
def delete_task(task_id: TASK_ID):
    """Delete a task."""
    db_session: Callable[[],
                         AbstractContextManager[Session]] = di["db_session_context"]

    with db_session() as db:
        if isinstance(db, Session):
            task = db.get(Task, task_id)

            if not task:
                rich_print(f"[red]Task {task_id} not found[/red]")
                return

            db.delete(task)
            db.commit()
            rich_print(f"[green]Task {task_id} deleted[/green]")


@app.command("update")
def update_task(
    task_id: TASK_ID,
    name: Optional[str] = Option(None, "--name", "-n"),
    description: Optional[str] = Option(None, "--description", "-d"),
    due_date: Optional[datetime] = Option(None, "--due"),
    complete: Optional[bool] = Option(None, "--complete", "-c"),
):
    """Update a task."""
    db_session: Callable[[],
                         AbstractContextManager[Session]] = di["db_session_context"]

    with db_session() as db:
        if isinstance(db, Session):
            task = db.get(Task, task_id)

            if not task:
                rich_print(f"[red]Task {task_id} not found[/red]")
                return

            if name:
                task.name = name
            if description:
                task.description = description
            if due_date:
                task.due_date = due_date
            if complete is not None:
                task.completed = complete

            db.commit()
            rich_print(f"[green]Task {task_id} updated[/green]")
