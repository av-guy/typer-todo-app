# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=redefined-outer-name
# pylint: disable=reimported

from os import path
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timedelta

from pytest import fixture
from kink import di

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

SCRIPT_PATH = path.abspath(__file__)
SCRIPT_DIR = path.dirname(SCRIPT_PATH)

DB_PATH = Path(SCRIPT_DIR + "/db")
DB_PATH.mkdir(exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{SCRIPT_DIR}/db/test_db.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@contextmanager
def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


di["db_session_context"] = override_get_db
di["db_url"] = SQLALCHEMY_DATABASE_URL

# Dependency injection must happen before BASE and Task are imported.
# Both of these modules depend on the "db_url" and "db_session_context".
from src.task_manager.database import BASE
from src.task_manager.models import Task

BASE.metadata.create_all(bind=engine)


@fixture
def test_task():
    db = TestingSessionLocal()

    task = Task(
        name="Water the baguettes",
        description="Strange dream",
        completed=False,
        due_date=datetime.now()
    )

    db.add(task)
    db.commit()

    task_2 = Task(
        name="Take the cat for a walk",
        description="This is impossible",
        completed=True,
        due_date=datetime.now()
    )

    db.add(task_2)
    db.commit()

    task_3 = Task(
        name="Go to the store",
        description="Need food",
        completed=False,
        due_date=datetime.now() + timedelta(days=1)
    )

    db.add(task_3)
    db.commit()

    yield task

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM tasks;"))
        connection.commit()
