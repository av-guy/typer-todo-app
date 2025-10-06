from typing import Sequence, Optional, Callable
from datetime import datetime
from contextlib import AbstractContextManager

from sqlalchemy.orm import Session
from kink import di

from ..models import Task


class SQLAlchemyTaskRepository:
    def __init__(self) -> None:
        self._db_context: Callable[[
        ], AbstractContextManager[Session]] = di["db_session_context"]

    def get(self, task_id: int) -> Optional[Task]:
        with self._db_context() as db:
            return db.get(Task, task_id)

    def complete(self, task_id: int):
        with self._db_context() as db:
            task = db.get(Task, task_id)
            if task:
                task.completed = True
                db.commit()

    def list(self) -> Sequence[Task]:
        with self._db_context() as db:
            return db.query(Task).all()

    def add(self, task: Task) -> int:
        with self._db_context() as db:
            db.add(task)
            db.commit()
            return task.id

    def delete(self, task: Task) -> None:
        with self._db_context() as db:
            db.delete(task)
            db.commit()

    def commit(self) -> None:
        with self._db_context() as db:
            db.commit()

    def filter_by_status(
        self,
        completed: Optional[bool] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
    ) -> Sequence[Task]:
        with self._db_context() as db:
            query = db.query(Task)

            if completed is not None:
                query = query.filter(Task.completed.is_(completed))
            if due_before is not None:
                query = query.filter(Task.due_date < due_before)
            if due_after is not None:
                query = query.filter(Task.due_date >= due_after)

            return query.all()
