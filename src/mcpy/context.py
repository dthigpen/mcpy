import contextlib
import textwrap
from typing import Iterator
from pathlib import Path
import json
from abc import ABC
from typing import IO, Callable
from pathlib import Path
from dataclasses import dataclass, field
import inspect
from .util import scoped_setattr

DEFAULT_HEADER_MSG = "Built with mcpy (https://github.com/dthigpen/mcpy)"


@dataclass
class Context:
    base_dir: Path
    sub_dir_stack: list[Path] = field(default_factory=list)
    namespace: str = None
    file_category: str = None
    file_name: str = None
    opened_file: IO = None
    input_handler: Callable = None

    def get_path(self) -> Path:
        """Get the current full path"""
        if not self.file_category:
            raise ValueError(
                "File category not set! (e.g. pack/data/namespace/<category>/etc)"
            )
        if not self.namespace:
            raise ValueError(
                "Namespace not set! (e.g. pack/data/<namespace>/functions/etc)"
            )

        path_dir = (
            self.base_dir
            / "data"
            / self.namespace
            / Path(self.file_category).joinpath(*self.sub_dir_stack)
        )
        if self.file_name:
            return path_dir / self.file_name
        return path_dir


def write(ctx, item: any) -> None:
    """Handle the given input depending on the current context"""
    if not ctx.input_handler:
        raise ValueError("Unknown context. Cannot handle input")
    ctx.input_handler(ctx, item)


def validate_files(ctx) -> None:
    if not ctx.opened_file or ctx.opened_file.closed:
        raise ValueError("No opened files to write to")
    if not ctx.file_name:
        raise ValueError("Cannot write to empty or unspecified file name")


def validate_not_in_file_context(ctx):
    if ctx.file_name is not None or ctx.opened_file is not None:
        raise ValueError(
            "Illegal state, already in a file context. Try reordering your contexts"
        )


def json_file_handler(ctx: Context, item: dict | str) -> None:
    validate_files(ctx)
    if isinstance(item, dict):
        item = json.dumps(item, indent=4)

    if isinstance(item, str) and not item.endswith("\n"):
        item += "\n"

    ctx.opened_file.write(item)


def mcfunction_handler(ctx: Context, item: str | list[str]):
    validate_files(ctx)

    def write_str(content: str):
        newline_count = content.count("\n")
        if content.endswith("\n"):
            newline_count -= 1

        # unindent indented multiline strings
        if newline_count > 0:
            content = textwrap.dedent(content)

        # add trailing newline if not present
        if not content.endswith("\n"):
            content += "\n"

        ctx.opened_file.write(content)

    if isinstance(item, list) or inspect.isgenerator(item):
        for content in item:
            write_str(str(content))
    else:
        write_str(str(item))


@contextlib.contextmanager
def dir(ctx: Context, name: str):
    validate_not_in_file_context(ctx)
    ctx.sub_dir_stack.append(Path(name))
    yield
    ctx.sub_dir_stack.pop()


@contextlib.contextmanager
def namespace(ctx: Context, name: str):
    validate_not_in_file_context(ctx)
    prev_namespace = ctx.namespace
    ctx.namespace = name
    (ctx.base_dir / "data" / ctx.namespace).mkdir(parents=True, exist_ok=True)
    yield
    ctx.namespace = prev_namespace


@contextlib.contextmanager
def file(
    ctx: Context,
    name: str,
    category=None,
    mode="w",
    header=False,
    ctx_handler=None,
    *args,
):
    with scoped_setattr(
        ctx,
        file_name=name,
        file_category=category,
        opened_file=ctx.opened_file,
        input_handler=ctx_handler if ctx_handler else ctx.input_handler,
    ):
        ctx.get_path().parent.mkdir(parents=True, exist_ok=True)
        with open(ctx.get_path(), mode, *args) as f:
            ctx.opened_file = f
            if header and mode == "w":
                f.write(f"# {DEFAULT_HEADER_MSG}\n\n")
            if ctx_handler:
                yield ctx.input_handler
            else:
                yield f


@contextlib.contextmanager
def mcfunction(ctx: Context, name: str, *args, **kwargs):
    if not name.endswith(".mcfunction"):
        name += ".mcfunction"
    with file(
        ctx,
        name,
        *args,
        category="functions",
        header=True,
        ctx_handler=mcfunction_handler,
        **kwargs,
    ) as f:
        yield f


@contextlib.contextmanager
def json_file(ctx: Context, name: str, *args, **kwargs):
    if not name.endswith(".json"):
        name += ".json"
    # JSON files can be in multiple file categories so let caller pass it in
    with file(ctx, name, *args, ctx_handler=json_file_handler, **kwargs) as f:
        yield f


@contextlib.contextmanager
def tag(ctx: Context, name: str, tag_type: str, *args, **kwargs):
    with dir(ctx, tag_type), json_file(
        ctx, name, category="tags", *args, **kwargs
    ) as f:
        yield f


@contextlib.contextmanager
def functions(ctx: Context, name: str, *args, **kwargs):
    with tag(ctx, name, "functions", *args, **kwargs) as f:
        yield f


@contextlib.contextmanager
def blocks(ctx: Context, name: str, *args, **kwargs):
    with tag(ctx, name, "blocks", *args, **kwargs) as f:
        yield f


@contextlib.contextmanager
def items(ctx: Context, name: str, *args, **kwargs):
    with tag(ctx, name, "items", *args, **kwargs) as f:
        yield f
