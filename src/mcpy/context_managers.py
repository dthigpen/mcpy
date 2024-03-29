import contextlib
from typing import Iterator
from pathlib import Path
from .context import (
    get_context,
    get_global_context,
    update_context,
)


@contextlib.contextmanager
def directory(name: str) -> Iterator[None]:
    """Create a directory in the datapack

    Args:
        name: The directory name

    Example:
        ``` python
        with directory('api'):
            with directory('foo/bar'):
                ...
        ```
    """
    ctx = get_context()
    with update_context(sub_dir_stack=(*ctx.sub_dir_stack, Path(name))):
        yield


@contextlib.contextmanager
def folder(name: str) -> Iterator[None]:
    """Create a directory in the datapack

    Args:
        name: The directory name

    Example:
    ``` python
    with folder('api'):
        with folder('foo/bar'):
            ...
    ```
    """
    with directory(name):
        yield


@contextlib.contextmanager
def namespace(name: str) -> Iterator[None]:
    """Create a namespace directory in the datapack

    Args:
        name: The namespace

    Example:
    ``` python
    with namespace('mypack'):
        ...
    ```
    """
    ctx = get_context()
    with update_context(namespace=name):
        ctx = get_context()
        (get_global_context().base_dir / "data" / ctx.namespace).mkdir(
            parents=True, exist_ok=True
        )
        yield
