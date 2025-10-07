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


def test_get_task(test_task: Task):
    repository = SQLAlchemyTaskRepository()
    task_item = repository.get(test_task.id)

    assert task_item is not None
    assert task_item.id == test_task.id
    assert task_item.description == test_task.description
    assert task_item.due_date == test_task.due_date
    assert task_item.name == test_task.name


@mark.parametrize("task_id, exc_type", [
    ("not_an_in", ValueError),
    (0, ValueError),
    (-1, ValueError),
])
def test_task_id_check(task_id: str | int, exc_type: Any):
    repository = SQLAlchemyTaskRepository()

    with raises(exc_type):
        repository.get(task_id)         # type: ignore

    with raises(exc_type):
        repository.complete(task_id)    # type: ignore


def test_task_complete(test_task: Task):
    repository = SQLAlchemyTaskRepository()
    repository.complete(test_task.id)

    with override_get_db() as db:
        task = db.get(Task, test_task.id)

        assert task is not None
        assert task.completed is True


def test_task_list(test_task: Task):
    repository = SQLAlchemyTaskRepository()
    task_list = repository.list()

    assert task_list
    assert len(task_list) == 3

    assert task_list[0].completed is False
    assert task_list[1].completed is True


def test_task_type_check():
    repository = SQLAlchemyTaskRepository()

    with raises(TypeError):
        repository.add(123)         # type: ignore

    with raises(TypeError):
        repository.delete(456)      # type: ignore


def test_add_task():
    repository = SQLAlchemyTaskRepository()

    task = Task(
        name="TaskName",
        description="TaskDescription",
        completed=False,
        due_date=datetime.now(),
    )

    task_id = repository.add(task)

    assert task_id is not None
    assert task_id == 1

    with override_get_db() as db:
        task = db.get(Task, task_id)

        assert task is not None
        assert task.id == 1
        assert task.name == "TaskName"
        assert task.description == "TaskDescription"
        assert task.completed is False


def test_delete_task(test_task: Task):
    repository = SQLAlchemyTaskRepository()

    task = None
    with override_get_db() as db:
        task = db.get(Task, test_task.id)

    assert task is not None
    repository.delete(task)

    with override_get_db() as db:
        task = db.get(Task, test_task.id)
        assert task is None


def test_update_task(test_task: Task):
    repository = SQLAlchemyTaskRepository()

    with override_get_db() as db:
        task = db.get(Task, test_task.id)
        assert task is not None

        task.name = "Updated Task"
        task.description = "Updated Description"
        task.completed = True

    repository.update(task)

    with override_get_db() as db:
        updated = db.get(Task, test_task.id)
        assert updated is not None
        assert updated.name == "Updated Task"
        assert updated.description == "Updated Description"
        assert updated.completed is True


@mark.parametrize(
    "completed, due_before, due_after, expected_count",
    [
        (True, None, None, 1),
        (False, None, None, 2),
        (None, datetime.now() + timedelta(days=1), None, 2),
        (None, None, datetime.now() - timedelta(days=1), 3)
    ],
)
def test_filter_by_status(
    test_task: Task,
    completed,
    due_before,
    due_after,
    expected_count
):
    repository = SQLAlchemyTaskRepository()

    results = repository.filter_by_status(
        completed=completed,
        due_before=due_before,
        due_after=due_after
    )

    assert isinstance(results, list)
    assert all(isinstance(t, Task) for t in results)
    assert len(results) == expected_count


@mark.parametrize(
    "kwargs",
    [
        {"completed": "yes"},
        {"due_before": "notadate"},
        {"due_after": 123},
    ],
)
def test_filter_by_status_invalid_types(kwargs):
    repository = SQLAlchemyTaskRepository()

    with raises(TypeError):
        repository.filter_by_status(**kwargs)
