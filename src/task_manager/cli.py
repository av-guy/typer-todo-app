# pylint: disable=import-outside-toplevel

from .bootstrap import initialize


def create_app():
    initialize()
    from .commands import todos
    return todos.app


app = create_app()
