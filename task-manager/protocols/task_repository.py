from typing import Protocol, Sequence, Optional
from datetime import datetime
from ..models import Task


class TaskRepository(Protocol):
    def get(self, task_id: int) -> Optional[Task]:
        ...

    def list(self) -> Sequence[Task]:
        ...

    def add(self, task: Task) -> None:
        ...

    def delete(self, task: Task) -> None:
        ...

    def complete(self, task_id: int) -> None:
        ...

    def filter_by_status(
        self,
        completed: Optional[bool] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
    ) -> Sequence[Task]:
        ...
