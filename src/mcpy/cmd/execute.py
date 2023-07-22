from .util import stringify, listify, tokens_to_str, file_path_to_mcfunction_path
from mcpy import Context, get_context, get_global_context, update_context, dir, mcfunction, write, switch_context
import contextlib
import dataclasses

@contextlib.contextmanager
def execute(conditions: str | list[str], limit=3):
    conditions = stringify(conditions)
    lines_buffer = []
    wrote_temp_file = False
    prev_ctx = get_context()
    gen_dir_name = get_global_context().config['generated_dir']
    with dir(gen_dir_name):

        gen_file_name = None
        counter = get_global_context().counter
        while gen_file_name is None or (get_context().get_path() / f'{gen_file_name}.mcfunction').exists():
            gen_file_name = f'gen_{prev_ctx.get_path().stem}{counter["generated_files"]}'
            counter["generated_files"] += 1

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
                    with switch_context(prev_ctx):
                        item = tokens_to_str('execute',conditions, 'run', item)
                        write(item)
                else:

                    lines_buffer.append(item)
                    if len(lines_buffer) > limit:
                        # write lines to temp file, then call in main file
                        with switch_context(gen_ctx):
                            for line in lines_buffer:
                                write(line)
                        with switch_context(prev_ctx):
                            write(tokens_to_str('execute',conditions, 'run',f'function {file_path_to_mcfunction_path(gen_path)}'))

                        lines_buffer = None
                        wrote_temp_file = True

            with update_context(input_handler=handle):
                yield
    if lines_buffer:
        with switch_context(prev_ctx):
            for line in lines_buffer:
                line = tokens_to_str('execute',conditions, 'run', line)
                write(line)

            