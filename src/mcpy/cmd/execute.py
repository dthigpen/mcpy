from .util import stringify, listify, tokens_to_str, file_path_to_mcfunction_path
from mcpy import Context, get_context, create_context, dir, mcfunction, write, open_context
import contextlib
import dataclasses

@contextlib.contextmanager
def execute(conditions: str | list[str], limit=3):
    conditions = stringify(conditions)
    lines_buffer = []
    wrote_temp_file = False
    prev_ctx = get_context()
    with dir('__generated__'):

        gen_file_name = None
        count = 0
        # TODO instead of checking file system it might be best to check a global state
        # so that files don't keep accumulating
        while count == 0 or (get_context().get_path() / f'{gen_file_name}.mcfunction').exists():
            gen_file_name = f'gen_{prev_ctx.get_path().stem}{count}'
            count += 1

        with mcfunction(gen_file_name):
            gen_ctx = get_context()
            gen_path = gen_ctx.get_path()
            def handle(ctx, item):
                nonlocal limit
                nonlocal conditions
                nonlocal lines_buffer
                nonlocal wrote_temp_file
                nonlocal prev_ctx
                if wrote_temp_file or limit is None:
                    with open_context(prev_ctx):
                        item = tokens_to_str('execute',conditions, 'run', item)
                        write(item)
                else:

                    lines_buffer.append(item)
                    if len(lines_buffer) > limit:
                        # write lines to temp file, then call in main file
                        with open_context(gen_ctx):
                            for line in lines_buffer:
                                write(line)
                        with open_context(prev_ctx):
                            write(tokens_to_str('execute',conditions, 'run',f'function {file_path_to_mcfunction_path(gen_path)}'))

                        lines_buffer = None
                        wrote_temp_file = True

            with create_context(input_handler=handle):
                yield
    if lines_buffer:
        with open_context(prev_ctx):
            item = tokens_to_str('execute',conditions, 'run', item)
            write(item)

            