# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-import

from pytest import fixture
from kink import di
from typer.testing import CliRunner

from src.task_manager.cli import app
from src.task_manager.repositories import SQLAlchemyTaskRepository
from src.task_manager.protocols import TaskRepository

from .utils import test_task, Task

runner = CliRunner()


@fixture(scope="session", autouse=True)
def setup_once():
    di[TaskRepository] = SQLAlchemyTaskRepository()


def test_app_run():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "create" in result.output


def test_list_tasks(test_task: Task):
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Water" in result.output


def test_complete_task(test_task: Task):
    result = runner.invoke(app, ["complete", "1"])
    assert result.exit_code == 0
    assert f"Task {test_task.id} marked complete" in result.output


def test_complete_bad_task_id(test_task: Task):
    result = runner.invoke(app, ["complete", "-10"])
    assert result.exit_code == 2
    assert "No such option" in result.output

    result = runner.invoke(app, ["complete", "0"])
    assert result.exit_code == 2
    assert "Invalid value" in result.output

    result = runner.invoke(app, ["complete", "999"])
    assert result.exit_code == 2
    assert "Task 999 not found" in result.output


def test_delete_task(test_task: Task):
    result = runner.invoke(app, ["delete", "1"])
    assert result.exit_code == 0
    assert "Task 1 deleted" in result.output


def test_delete_bad_task_id(test_task: Task):
    result = runner.invoke(app, ["delete", "-10"])
    assert result.exit_code == 2
    assert "No such option" in result.output

    result = runner.invoke(app, ["delete", "0"])
    assert result.exit_code == 2
    assert "Invalid value" in result.output

    result = runner.invoke(app, ["delete", "999"])
    assert result.exit_code == 2
    assert "Task 999 not found" in result.output


def test_create_task():
    result = runner.invoke(
        app,
        [
            "create",
            "Coffee",
            "2025-12-31T12:00:00",
            "--description",
            "Morning brew",
        ],
    )
    assert result.exit_code == 0
    assert "Task created with ID" in result.output


def test_update_task(test_task: Task):
    result = runner.invoke(
        app,
        [
            "update",
            str(test_task.id),
            "--name",
            "Updated Task",
            "--description",
            "Updated description",
            "--complete",
            "--due",
            "2025-12-31T12:00:00",
        ],
    )

    assert result.exit_code == 0
    assert f"Task {test_task.id} updated" in result.output

def test_update_bad_task_id(test_task: Task):
    result = runner.invoke(
        app,
        [
            "update",
            "-10",
            "--name",
            "Updated Task",
            "--description",
            "Updated description",
            "--complete",
            "--due",
            "2025-12-31T12:00:00",
        ],
    )

    assert result.exit_code == 2
    assert "No such option" in result.output

    result = runner.invoke(
        app,
        [
            "update",
            "0",
            "--name",
            "Updated Task",
            "--description",
            "Updated description",
            "--complete",
            "--due",
            "2025-12-31T12:00:00",
        ],
    )
    assert result.exit_code == 2
    assert "Invalid value" in result.output

    result = runner.invoke(
        app,
        [
            "update",
            "999",
            "--name",
            "Updated Task",
            "--description",
            "Updated description",
            "--complete",
            "--due",
            "2025-12-31T12:00:00",
        ],
    )
    assert result.exit_code == 2
    assert "Task 999 not found" in result.output
