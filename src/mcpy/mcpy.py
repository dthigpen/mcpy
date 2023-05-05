import argparse
import importlib
from typing import Callable
from pathlib import Path
from timeit import default_timer as timer
import traceback
from datetime import timedelta
from .context import Context, write

from watchfiles import watch

def module_attr(module_attr_str: str) -> tuple:
    # accepts values such as:
    # path.sub:funct, path/sub:funct, path.sub.funct, etc
    module_attr_str = module_attr_str.replace('/','.').replace(':','.')
    if "." not in module_attr_str:
        raise argparse.ArgumentTypeError(
            "Bad module run specifier. Use format <module.sub>:<run_function> format"
        )
    name, attr = module_attr_str.rsplit(".", 1)
    return name, attr


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build mcpy datapacks!")
    parser.add_argument(
        "entrypoint",
        type=module_attr,
        help='"<module>:<attr>" string to call your datapack building function. e.g. for my_pack.py with a run function: my_pack:run',
    )
    parser.add_argument(
        "-w", "--watch", action="store_true", help="watch file changes and rebuild"
    )
    return parser.parse_args()


def __get_base_dir(base_dir: Path=None) -> Path:
    if base_dir is None:
        cwd = Path.cwd()
        if cwd.joinpath("pack.mcmeta").is_file():
            base_dir = cwd
        elif cwd.parent.joinpath("pack.mcmeta").is_file():
            base_dir = cwd.parent
        else:
            raise ValueError(
                "Must run from either the root of the datapack directory or inside the datapack-dir/src folder. Or manually pass in a directory with base_dir=<Path>"
            )
    return Path.cwd() if base_dir is None else Path(base_dir)


def build(*builder_fns: Callable[[Context],None]):
        for builder in builder_fns:
            ctx = Context(__get_base_dir())
            items = builder(ctx)
            if items:
                for item in items:
                    write(ctx, item)
def main():
    args = get_args()
    module_name, entrypoint_fn_name = args.entrypoint
    entrypoint_mod = importlib.import_module(module_name)
    
    def timed_build(runner_fn):
        print("Starting build...")
        start = timer()
        build(runner_fn)
        end = timer()
        delta = timedelta(seconds=end - start)
        print(f"Build time: {delta}")

    timed_build(getattr(entrypoint_mod, entrypoint_fn_name))
    if args.watch:
        mod_path = Path(entrypoint_mod.__file__)
        print(f"Watching files in {mod_path.parent}")
        print("Press Ctrl-C to stop at anytime")
        for changes in watch(mod_path.parent, raise_interrupt=False):
            try:
                entrypoint_mod = importlib.reload(entrypoint_mod)
                runner = getattr(entrypoint_mod, entrypoint_fn_name)
                timed_build(runner)
            except KeyboardInterrupt as e:
                raise e
            except Exception:
                print(traceback.format_exc())
