from .util import stringify, tokens_to_str
from ..context import (
    get_context,
    get_global_context,
    update_context,
    switch_context,
    write,
)
from ..context_managers import directory
from ..decorators import mcfunction
from pathlib import Path
import contextlib


def __create_file_name(directory: Path, base_file_name: str) -> str:
    gen_file_name = None
    counter = get_global_context().counter
    while gen_file_name is None or (directory / f"{gen_file_name}.mcfunction").exists():
        gen_file_name = f'{base_file_name}_{counter["generated_files"]}'
        counter["generated_files"] += 1
    return gen_file_name


@contextlib.contextmanager
def execute(*conditions: str, limit: int = 3):
    """Context manager to execute the inner statements with the given conditions

    Args:
        conditions: execute conditions e.g. if, unless, store, etc to apply to each command
        limit: the maximum number of inline commands to allow before creating a generated mcfunction file
    """
    conditions = stringify(conditions)
    lines_buffer = []
    prev_ctx = get_context()
    file_name = prev_ctx.get_path().stem
    gen_dir_name = get_global_context().config["generated_dir"]
    gen_ctx = None

    def handle(ctx, item):
        nonlocal limit
        nonlocal conditions
        nonlocal lines_buffer
        nonlocal prev_ctx
        nonlocal gen_ctx
        # always write inline to current mcfunction
        if limit is None:
            with switch_context(prev_ctx):
                item = tokens_to_str("execute", conditions, "run", item)
                write(item)
        # if already wrote to generated file, continue writing lines to it
        elif gen_ctx:

            @mcfunction(name=Path(gen_ctx.file_name).stem, mode="w")
            def __gen_fn():
                write(item)

        else:
            lines_buffer.append(item)
            if len(lines_buffer) > limit:
                with directory(gen_dir_name):
                    # determine file name
                    gen_file_name = __create_file_name(
                        get_context().get_path(), file_name
                    )

                    # write buffer to generated file
                    @mcfunction(name=gen_file_name)
                    def __gen_fn():
                        nonlocal gen_ctx
                        gen_ctx = get_context()
                        for line in lines_buffer:
                            write(line)

                    with switch_context(prev_ctx):
                        write(
                            tokens_to_str(
                                "execute",
                                conditions,
                                "run",
                                f"function {gen_ctx.get_resource_path()}",
                            )
                        )

                lines_buffer = None

    with update_context(input_handler=handle):
        yield
    if lines_buffer:
        with switch_context(prev_ctx):
            for line in lines_buffer:
                line = tokens_to_str("execute", conditions, "run", line)
                write(line)


def if_(*conditions: str) -> str:
    fragments = []
    for cond in conditions:
        fragments.append(f"if {cond}")
    return stringify(fragments)


def unless(*conditions: str) -> str:
    fragments = []
    for cond in conditions:
        fragments.append(f"unless {cond}")
    return stringify(fragments)
