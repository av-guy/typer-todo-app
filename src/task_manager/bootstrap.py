# pylint: disable=import-outside-toplevel

from os import getenv, path
from pathlib import Path
from kink import di


def initialize():
    script_path = path.abspath(__file__)
    script_directory = path.dirname(script_path)
    db_path = Path(script_directory + "/db")

    if not db_path.exists():
        db_path.mkdir()

    DEFAULT_DB_URL = f"sqlite:///{script_directory}/db/todos_db.db"
    di["db_url"] = getenv("DATABASE_URL", DEFAULT_DB_URL)

    from .database import get_db, BASE, ENGINE
    BASE.metadata.create_all(bind=ENGINE)
    di["db_session_context"] = get_db

    from .repositories import SQLAlchemyTaskRepository
    from .protocols import TaskRepository
    di[TaskRepository] = SQLAlchemyTaskRepository()
