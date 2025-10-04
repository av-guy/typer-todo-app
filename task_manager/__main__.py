# pylint: disable=wrong-import-order

from . import bootstrap

from typer import Typer
from .commands import todos


app = Typer()
app.add_typer(todos.app, name="todos")


if __name__ == "__main__":
    bootstrap.initialize()
    app()
