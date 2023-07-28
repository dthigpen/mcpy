import contextlib
import textwrap
from typing import Iterator, Literal, Callable
from pathlib import Path
import json
from typing import IO, Callable
from pathlib import Path
from dataclasses import dataclass, field, replace
import inspect
import contextvars
from collections import defaultdict

__CONTEXT = contextvars.ContextVar("mcpy.context")
__GLOBAL = contextvars.ContextVar("mcpy.global_context")


@dataclass(frozen=True)
class GlobalContext:
    base_dir: Path
    config: dict
    counter: defaultdict[int] = field(
        default_factory=lambda: defaultdict(int), init=False
    )

    def increment_count(self, key: str) -> int:
        """Get the current count then increment the counter"""
        count = self.counter[key]
        self.counter[key] += 1
        return count


@dataclass(frozen=True)
class Context:
    """
    A class to represent the state of the datapack.
    """

    sub_dir_stack: tuple[Path] = field(default_factory=tuple)
    namespace: str = None
    file_category: str = None
    file_name: str = None
    opened_file: IO = None
    input_handler: Callable = None

    def get_resource_path(self) -> str:
        if not self.file_category:
            raise ValueError(
                "File category not set! (e.g. pack/data/namespace/<category>/etc)"
            )
        if not self.namespace:
            raise ValueError(
                "Namespace not set! (e.g. pack/data/<namespace>/functions/etc)"
            )
        path_items = (*map(lambda p: str(p), self.sub_dir_stack), Path(self.file_name).stem)
        return f'{self.namespace}:{"/".join(path_items)}'
    def get_path(self) -> Path:
        """Returns the current full path in the datapack"""

        if not self.file_category:
            raise ValueError(
                "File category not set! (e.g. pack/data/namespace/<category>/etc)"
            )
        if not self.namespace:
            raise ValueError(
                "Namespace not set! (e.g. pack/data/<namespace>/functions/etc)"
            )

        path_dir = (
            get_global_context().base_dir
            / "data"
            / self.namespace
            / Path(self.file_category).joinpath(*self.sub_dir_stack)
        )
        if self.file_name:
            return path_dir / self.file_name
        return path_dir

    def write(self, item: any) -> None:
        """Handle the given input depending on the current context"""
        if not self.input_handler:
            raise ValueError("Unknown context. Cannot handle input")
        self.input_handler(self, item)


def write(item: any) -> None:
    """Handle the given input depending on the current context"""
    ctx = get_context()
    if not ctx.input_handler:
        raise ValueError("Unknown context. Cannot handle input")
    if inspect.isgenerator(item):
        for content in item:
            ctx.input_handler(ctx, content)
    else:
        ctx.input_handler(ctx, item)






def get_context() -> Context:
    """Get the current context of the datapack

    Returns:
        Current context object

    """
    return __CONTEXT.get()


def get_global_context() -> GlobalContext:
    return __GLOBAL.get()


@contextlib.contextmanager
def switch_context(ctx: Context):
    token = __CONTEXT.set(ctx)
    yield
    __CONTEXT.reset(token)


@contextlib.contextmanager
def init_context(base_dir: Path, config: dict, **initial_ctx_args: any):
    """Underlying context manager for creating an initial datapack context

    Args:
        base_dir: datapack base directory
        config: datapack config
        initial_ctx_args: initial values to apply to the context
    """
    __GLOBAL.set(GlobalContext(base_dir, config))
    ctx = Context(**initial_ctx_args)
    with switch_context(ctx):
        yield


@contextlib.contextmanager
def update_context(**context_changes: any):
    """Underlying context manager for making changes to the current context

    Args:
        context_changes: changes to apply to the new context
    """
    ctx = get_context()
    with switch_context(replace(ctx, **context_changes)):
        yield



