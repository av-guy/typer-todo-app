from typing import Sequence, Optional, Callable
from datetime import datetime
from contextlib import AbstractContextManager

from sqlalchemy.orm import Session
from kink import inject

from ..models import Task
from ..protocols import TaskRepository


@inject(alias=TaskRepository)
class SQLAlchemyTaskRepository:
    def __init__(self, db_session_context: Callable[[
    ], AbstractContextManager[Session]]) -> None:
        self._db_context = db_session_context

    def _task_id_check(self, task_id: int) -> None:
        if not isinstance(task_id, int):
            raise ValueError("Task ID must be an integer.")

        if task_id < 1:
            raise ValueError("Task ID must be greater than 0.")

    def _task_type_check(self, task: Task) -> None:
        if not isinstance(task, Task):
            raise TypeError("`task` must be of type Task.")

    def get(self, task_id: int) -> Optional[Task]:
        self._task_id_check(task_id)

        with self._db_context() as db:
            return db.get(Task, task_id)

    def complete(self, task_id: int) -> None:
        self._task_id_check(task_id)

        with self._db_context() as db:
            task = db.get(Task, task_id)
            if task:
                task.completed = True
                db.commit()

    def list(self) -> Sequence[Task]:
        with self._db_context() as db:
            return db.query(Task).all()

    def add(self, task: Task) -> int | None:
        self._task_type_check(task)

        with self._db_context() as db:
            db.add(task)
            db.commit()
            return task.id

    def delete(self, task: Task) -> None:
        self._task_type_check(task)

        with self._db_context() as db:
            db.delete(task)
            db.commit()

    def update(self, task: Task) -> None:
        self._task_type_check(task)

        with self._db_context() as db:
            existing_task = db.get(Task, task.id)

            if existing_task is not None:
                existing_task.name = task.name
                existing_task.completed = task.completed
                existing_task.due_date = task.due_date
                existing_task.description = task.description

            db.commit()

    def filter_by_status(
        self,
        completed: Optional[bool] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
    ) -> Sequence[Task]:
        if completed is not None and not isinstance(completed, bool):
            raise TypeError("`completed` must be a boolean or None.")

        if due_before is not None and not isinstance(due_before, datetime):
            raise TypeError("`due_before` must be a datetime or None.")

        if due_after is not None and not isinstance(due_after, datetime):
            raise TypeError("`due_after` must be a datetime or None.")

        with self._db_context() as db:
            query = db.query(Task)

            if completed is not None:
                query = query.filter(Task.completed.is_(completed))

            if due_before is not None:
                query = query.filter(Task.due_date < due_before)

            if due_after is not None:
                query = query.filter(Task.due_date >= due_after)

            return query.all()
