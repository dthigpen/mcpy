import contextlib
import textwrap
from typing import Iterator, Literal
from pathlib import Path
import json
from typing import IO, Callable
from pathlib import Path
from dataclasses import dataclass, field, replace
import inspect
import contextvars


DEFAULT_HEADER_MSG = "Built with mcpy (https://github.com/dthigpen/mcpy)"

__CONTEXT = contextvars.ContextVar('mcpy.context')

@dataclass(frozen=True)
class Context:
    '''
    A class to represent the state of the datapack.
    '''
    base_dir: Path
    sub_dir_stack: tuple[Path] = field(default_factory=tuple)
    namespace: str = None
    file_category: str = None
    file_name: str = None
    opened_file: IO = None
    input_handler: Callable = None

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
            self.base_dir
            / "data"
            / self.namespace
            / Path(self.file_category).joinpath(*self.sub_dir_stack)
        )
        if self.file_name:
            return path_dir / self.file_name
        return path_dir


def write(item: any) -> None:
    """Handle the given input depending on the current context"""
    ctx = get_context()
    if not ctx.input_handler:
        raise ValueError("Unknown context. Cannot handle input")
    ctx.input_handler(ctx, item)


def __validate_files(ctx) -> None:
    if not ctx.opened_file or ctx.opened_file.closed:
        raise ValueError("No opened files to write to")
    if not ctx.file_name:
        raise ValueError("Cannot write to empty or unspecified file name")


def __validate_not_in_file_context(ctx):
    if ctx.file_name is not None or ctx.opened_file is not None:
        raise ValueError(
            "Illegal state, already in a file context. Try reordering your contexts"
        )


def __json_file_handler(ctx: Context, item: dict | str) -> None:
    __validate_files(ctx)
    if isinstance(item, dict):
        item = json.dumps(item, indent=4)

    if isinstance(item, str) and not item.endswith("\n"):
        item += "\n"

    ctx.opened_file.write(item)


def __mcfunction_handler(ctx: Context, item: str | list[str]):
    __validate_files(ctx)

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
def dir(name: str) -> Iterator[None]:
    '''Create a directory in the datapack
    
    Args:
        ctx: The datapack context to apply the directory
        name: The directory name
    
    '''
    ctx = get_context()
    __validate_not_in_file_context(ctx)
    with create_context(sub_dir_stack=(*ctx.sub_dir_stack, Path(name))):
        yield


def get_context() -> Context:
    return __CONTEXT.get()

def set_context(ctx: Context) -> contextvars.Token:
    return __CONTEXT.set(ctx)


@contextlib.contextmanager    
def create_context(**context_changes):
    try:
        ctx = __CONTEXT.get()
    except LookupError as e:
        ctx = Context(None)
    token = __CONTEXT.set(replace(ctx, **context_changes))
    yield
    __CONTEXT.reset(token)

@contextlib.contextmanager
def namespace(name: str) -> Iterator[None]:
    '''Create a namespace directory in the datapack
    
    Args:
        ctx: The datapack context to apply the namespace
        name: The namespace
    
    '''
    ctx = get_context()
    __validate_not_in_file_context(ctx)
    with create_context(namespace=name):
        ctx = get_context()
        (ctx.base_dir / "data" / ctx.namespace).mkdir(parents=True, exist_ok=True)
        yield


@contextlib.contextmanager
def file(
    name: str,
    category: Literal['functions', 'tags', 'blocks','items, advancements']=None,
    mode: str="w",
    header: bool=False,
    ctx_handler: Callable[[Context, any],None]=None,
    *args,
) -> Iterator[None]:
    '''Underlying function to create a file in the datapack
    
    See mcfunction, functions, blocks, etc to write specific types.
    
    Args:
        name: The file name
        category: the category of file. E.g. functions, tags, blocks, items, advancements
    
    '''
    ctx = get_context()
    with create_context(file_name=name,
        file_category=category,
        input_handler=ctx_handler if ctx_handler else ctx.input_handler):
        ctx = get_context()
        ctx.get_path().parent.mkdir(parents=True, exist_ok=True)
        with open(ctx.get_path(), mode, *args) as f:
            with create_context(opened_file=f):
                if header and mode == "w":
                    f.write(f"# {DEFAULT_HEADER_MSG}\n\n")
                yield


@contextlib.contextmanager
def tag(name: str, tag_type: str) -> Iterator[None]:
    '''Underlying function to create a tag file in the datapack
    
    Args:
        name: The name of the file
        tag_type: The type of the tag file. E.g. functions, items, etc

    '''
    with dir(tag_type), json_file(name, category="tags"
    ) as f:
        yield f


@contextlib.contextmanager
def mcfunction(name: str) -> Iterator[None]:
    '''Create an mcfunction file in the datapack
    
    Args:
        name: The name of the file
    '''
    if not name.endswith(".mcfunction"):
        name += ".mcfunction"
    with file(
        name,
        category="functions",
        header=True,
        ctx_handler=__mcfunction_handler,
    ) as f:
        yield f


@contextlib.contextmanager
def json_file(name: str, *args, **kwargs) -> Iterator[None]:
    '''Create a JSON file in the datapack
    
    Args:
        name: The name of the file
        *args: Additional arguments to be passed to the base file context manager
        **kwargs: Additional keyword arguments to be passed to the base file context manager
    '''
    if not name.endswith(".json"):
        name += ".json"
    
    # JSON files can be in multiple file categories so let caller pass it in
    with file(name, *args, ctx_handler=__json_file_handler, **kwargs):
        yield


@contextlib.contextmanager
def functions(name: str) -> Iterator[None]:
    '''Create a functions tag file in the datapack
    
    Args:
        name: The name of the file
    '''
    with tag( name, "functions"):
        yield


@contextlib.contextmanager
def blocks(name: str) -> Iterator[None]:
    '''Create a blocks tag file in the datapack
    
    Args:
        name: The name of the file
    '''
    with tag(name, "blocks"):
        yield


@contextlib.contextmanager
def items(name: str) -> Iterator[None]:
    '''Create an items tag file in the datapack
    
    Args:
        name: The name of the file
    '''
    with tag(name, "items"):
        yield
