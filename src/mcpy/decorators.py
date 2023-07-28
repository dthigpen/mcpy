import json
import textwrap
from typing import Iterator, Literal, Callable
from typing import  Callable
from dataclasses import dataclass
from .context import (
    Context,
    get_context,
    update_context,
    write
)
from .context_managers import (
    directory
)
import inspect

DEFAULT_HEADER_MSG = "Built with mcpy (https://github.com/dthigpen/mcpy)"

@dataclass
class Resource:
    path: str

    def __str__(self) -> str:
            return self.path

@dataclass
class FunctionResource(Resource):

    def __call__(self) -> None:
        write(f"function {self}")

def __validate_files(ctx) -> None:
    if not ctx.opened_file or ctx.opened_file.closed:
        raise ValueError("No opened files to write to")
    if not ctx.file_name:
        raise ValueError("Cannot write to empty or unspecified file name")


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



def file(
    generator_fn: Callable[[],Iterator]=None,
    *,
    name:str=None,
    category: Literal["functions", "tags", "blocks", "items, advancements"] = None,
    mode: str = "w",
    header: bool = False,
    ctx_handler: Callable[[Context, any], None] = None,
) -> Resource:
    """Underlying function to create a file in the datapack

    See mcfunction, functions, blocks, etc to write specific types.
    
    Args:
        generator_fn: Generator function to build the file from
        name: The file name
        category: the category of file. E.g. functions, tags, blocks, items, advancements

    Returns:
        resource_path: The resource path to the file created in this context
    """

    # decorator to write out function contents immediately
    def decorator_file(func):
        nonlocal name
        if name is None:
            name = func.__name__
        ctx = get_context()
        with update_context(
            file_name=name,
            file_category=category,
            input_handler=ctx_handler if ctx_handler else ctx.input_handler,
        ):
            ctx = get_context()
            ctx.get_path().parent.mkdir(parents=True, exist_ok=True)
            with open(ctx.get_path(), mode) as f:
                with update_context(opened_file=f):
                    if header and mode == "w":
                        write(f"# {DEFAULT_HEADER_MSG}\n\n")
                    items = func()
                    if items:
                        for item in items:
                            write(item)
                    resource_path = get_context().get_resource_path()
            
            return Resource(resource_path)

    if generator_fn is None:
        return decorator_file
    else:
        return decorator_file(generator_fn)


def tag(generator_fn: Callable[[],Iterator]=None, *, tag_type: Literal["functions", "tags", "blocks", "items, advancements"]=None, name: str = None, **kwargs: any) -> Iterator[str]:
    """Decorator to create a generic tag file.

    The generator function can yield JSON structures (usually a dict) or call write(<data>).

    Args:
        generator_fn: Generator function to build the file from
        tag_type: The resource category of the tag
        name: The name of the file, overrides the decorated function's name
        kwargs: extra arguments to be passed to the underlying file function

    Example:
        ``` py
        @tag('some_future_tag')
        def my_tag():
            yield {
                "values": ["foo", "bar"]
            }
        ```
    """

    def decorator_tag(func):
        with directory(tag_type):
            return json_file(func, name=name, category="tags", **kwargs)

    if generator_fn is None:
        return decorator_tag
    else:
        return decorator_tag(generator_fn)


def mcfunction(generator_fn: Callable[[],Iterator]=None, *, name:str = None, **kwargs: any):
    """A decorator for creating an mcfunction file.
    
    The generator function can yield command strings or call write(<cmd>)

    Args:
        generator_fn: Generator function to build the file from
        name: The name of the file, overrides the decorated function's name
        kwargs: extra arguments to be passed to the underlying file function

    Example:
        ``` py
        @mcfunction
        def greet():
            yield 'say Hello'
            write('say World!')
            yield 'Goodbye!'
        ```
    """
    def decorator_mcfunction(func):
        nonlocal name
        if name is None:
            name = func.__name__
        if not name.endswith(".mcfunction"):
            name += ".mcfunction"
        file_resource = file(
            func,
            name=name,
            category="functions",
            header=True,
            ctx_handler=__mcfunction_handler,
            **kwargs,
        )

        return FunctionResource(file_resource.path)

    if generator_fn is None:
        return decorator_mcfunction
    else:
        return decorator_mcfunction(generator_fn)


def json_file(generator_fn: Callable[[],Iterator]=None, *, category: Literal["functions", "tags", "blocks", "items, advancements"]=None, name: str=None, **kwargs: any) -> Iterator[str]:
    """Decorator to create a JSON file.

    The generator function can yield JSON structures (usually a dict) or call write(<data>).

    Args:
        generator_fn: Generator function to build the file from
        category: The type of JSON resource, used in file path
        name: The name of the file, overrides the decorated function's name
        kwargs: extra arguments to be passed to the underlying file function

    Example:
        ``` py
        @jsonfile('tags')
        def my_tag():
            yield {
                "values": ["value1", "value2", "value3"]
            }
        ```
    """

    def decorator_mcfunction(func):
        nonlocal name
        if name is None:
            name = func.__name__
        if not name.endswith(".json"):
            name += ".json"
        return file(
            func,
            category=category,
            name=name,
            ctx_handler=__json_file_handler,
            **kwargs,
        )

    if generator_fn is None:
        return decorator_mcfunction
    else:
        return decorator_mcfunction(generator_fn)



def functions(generator_fn: Callable[[],Iterator]=None, *, name:str=None, **kwargs: any) -> Iterator[str]:
    """Decorator to create a functions tag file.

    The generator function can yield JSON structures (usually a dict) or call write(<data>).

    Args:
        generator_fn: Generator function to build the file from
        name: The name of the file, overrides the decorated function's name
        kwargs: extra arguments to be passed to the underlying file function

    Example:
        ``` py
        @functions
        def load():
            yield {
                "values": ["dep_pack:tick", "my_pack:tick"]
            }
        ```
    """

    def decorator_mcfunction(func):
        return tag(func, tag_type="functions", name=name, **kwargs)

    if generator_fn is None:
        return decorator_mcfunction
    else:
        return decorator_mcfunction(generator_fn)


def blocks(generator_fn: Callable[[],Iterator]=None, *, name:str=None, **kwargs: any) -> Iterator[str]:
    """Decorator to create a blocks tag file.

    The generator function can yield JSON structures (usually a dict) or call write(<data>).

    Args:
        generator_fn: Generator function to build the file from
        name: The name of the file, overrides the decorated function's name
        kwargs: extra arguments to be passed to the underlying file function

    Example:
        ``` py
        @blocks
        def transparent_blocks():
            yield {
                "values": ["minecraft:glass", "minecraft:air"]
            }
        ```
    """

    def decorator_mcfunction(func):
        return tag(func, tag_type="blocks", name=name, **kwargs)

    if generator_fn is None:
        return decorator_mcfunction
    else:
        return decorator_mcfunction(generator_fn)


def items(generator_fn: Callable[[],Iterator]=None, *, name:str=None, **kwargs: any) -> Iterator[str]:
    """Decorator to create an items tag file.

    The generator function can yield JSON structures (usually a dict) or call write(<data>).

    Args:
        generator_fn: Generator function to build the file from
        name: The name of the file, overrides the decorated function's name
        kwargs: extra arguments to be passed to the underlying file function

    Example:
        ``` py
        @items
        def cool_items():
            yield {
                "values": ["minecraft:stick", "minecraft:apple"]
            }
        ```
    """

    def decorator_mcfunction(func):
        return tag(func, tag_type="items", name=name, **kwargs)

    if generator_fn is None:
        return decorator_mcfunction
    else:
        return decorator_mcfunction(generator_fn)
