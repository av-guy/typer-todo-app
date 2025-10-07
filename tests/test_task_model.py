# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=wrong-import-order

from typing import Any
from pytest import mark, raises
from datetime import datetime, timedelta

from .utils import test_task, override_get_db

from src.task_manager.repositories import SQLAlchemyTaskRepository
from src.task_manager.models import Task


def stringify_task(task: Task):
    return (
        f"Task(id={task.id!r}, name={task.name!r}, completed={task.completed!r}, "
        f"due_date={task.due_date!r})"
    )


def test_task_repr(test_task):
    task_str = repr(test_task)
    assert task_str == stringify_task(test_task)
