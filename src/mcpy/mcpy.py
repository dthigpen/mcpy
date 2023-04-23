import argparse
import importlib
from typing import Callable
from pathlib import Path
from timeit import default_timer as timer
from datetime import timedelta

from watchfiles import watch

def module_attr(module_attr_str: str) -> tuple:
    if ":" not in module_attr_str:
        raise argparse.ArgumentTypeError(
            "Bad module run specifier. Use format <module.sub>:<run_function> format"
        )
    name, attr = module_attr_str.split(":", 1)
    mod = importlib.import_module(name)
    return mod, getattr(mod, attr)


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


def run(entrypoint_fn: Callable):
    entrypoint_fn()


def main():
    args = get_args()
    entrypoint_mod, entrypoint_fn = args.entrypoint
    def timed_build():
        print('Starting build...')
        start = timer()
        run(entrypoint_fn)
        end = timer()
        delta = timedelta(seconds=end-start)
        print(f'Build time: {delta}')
    timed_build()
    if args.watch:
        mod_path = Path(entrypoint_mod.__file__)
        print(f'Watching files in {mod_path.parent}')
        print('Press Ctrl-C to stop at anytime')
        for changes in watch(mod_path.parent):
            timed_build()
    
