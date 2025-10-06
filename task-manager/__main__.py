# pylint: disable=wrong-import-order

from . import bootstrap
from .commands import todos


app = todos.app


if __name__ == "__main__":
    bootstrap.initialize()
    app()
