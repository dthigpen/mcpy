import argparse
import importlib
from typing import Callable
from types import ModuleType
from pathlib import Path
from timeit import default_timer as timer
import traceback
from datetime import timedelta
from .context import Context, write
import functools
import json
from watchfiles import watch

import dpbuild


def datapack(func):
    @functools.wraps(func)
    def datapack_wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    datapack_wrapper.mcpy_datapack = True
    return datapack_wrapper

class Datapack:
    def __init__(self, path: str | Path) -> None:
        self.path = valid_datapack_path(path)

    def build(self, changed_files: list[Path]) -> None:
        pass


class McpyDatapack(Datapack):
    def __init__(self, path) -> None:
        super().__init__(path)
        valid_mcpy_datapack_path(path)
        self.module = None

    def get_config(self) -> dict:
        config_file_name = "mcpy_config.json"
        config = {"entrypoint": "pack.py"}
        config_file_path = None
        if (p := self.path / config_file_name).is_file():
            config_file_path = p
        elif (p := self.path / "src" / config_file_name).is_file():
            config_file_path = p
        # TODO lastly check inside module folder with glob
        if config_file_path:
            with open(config_file_path) as f:
                config = json.load(f)
        return config

    def get_module_path(self) -> Path:
        config = self.get_config()
        if "entrypoint" in config:
            pack_file_name = config["entrypoint"]
            if (p := self.path / pack_file_name).is_file():
                return p
            if (p := self.path / "src" / pack_file_name).is_file():
                return p
            res = (self.path / "src").glob(f"*/{pack_file_name}")
            if res:
                return next(res)
        raise ValueError("Unable to find entrypoint .py file!")

    def build(self, output_dir=None) -> None:
        if not output_dir:
            output_dir = self.path
        if not self.module:
            module_path = self.get_module_path()
            module_name = str(module_path.parent / module_path.stem).replace("/", ".")
            self.module = importlib.import_module(module_name)
        else:
            self.module = importlib.reload(self.module)

        marked_functions = [
            f
            for _, f in self.module.__dict__.items()
            if callable(f) and hasattr(f, "mcpy_datapack") and f.mcpy_datapack is True
        ]
        if len(marked_functions) == 0:
            raise ValueError(
                "No entrypoint found. Use @mcpy.entrypoint decorator to specify an entrypoint"
            )
        if len(marked_functions) > 1:
            raise ValueError("More than one entrypoint found. Only one is allowed")

        build(marked_functions[0], output_dir)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build mcpy datapacks!")
    parser.add_argument(
        "mcpy_datapack",
        nargs="?",
        type=McpyDatapack,
        default=".",
        help="mcpy python file",
    )
    parser.add_argument(
        "-w", "--watch", action="store_true", help="watch file changes and rebuild"
    )
    parser.add_argument(
        "-o", "--output-dir", type=Path, help="Directory to put compiled datapack"
    )
    return parser.parse_args()


def __get_base_dir(base_dir: Path = None) -> Path:
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


def build(builder_fn: Callable[[Context], None], output_dir: Path):
    ctx = Context(__get_base_dir(output_dir))
    items = builder_fn(ctx)
    if items:
        for item in items:
            write(ctx, item)


def valid_datapack_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"Path to datapack does not exist: {path}")

    mc_meta_file = path / "pack.mcmeta"
    if not mc_meta_file.is_file():
        raise argparse.ArgumentTypeError(
            f"Datapack does not have a pack.mcmeta file: {mc_meta_file}"
        )

    return path


def valid_mcpy_datapack_path(path_str: str) -> Path:
    path = valid_datapack_path(path_str)

    if (
        path.glob("*.py")
        or (path / "src").glob("*.py")
        or (path / "src").glob("*/*.py")
    ):
        return path
    raise argparse.ArgumentTypeError(
        f"Datapack does not contain a .py file at {path.name}, {path / 'src'} or {path / 'src' / 'module'}"
    )


def output_bundled(output_dir: Path, datapack_paths: list[Path]):
    print("bundling")
    if output_dir:
        dpbuild.run([datapack_paths], output_dir, strict=True)

def main():
    args = get_args()
    datapack = args.mcpy_datapack

    def timed_build():
        print(f"Building {datapack.path}")
        start = timer()
        datapack.build(output_dir = args.output_dir)
        end = timer()
        delta = timedelta(seconds=end - start)
        print(f"Build time: {delta}")
    
    timed_build()
    
    if args.watch:
        print(f"Watching files")
        print("Press Ctrl-C to stop at anytime")
        for _ in watch(datapack.get_module_path().parent, raise_interrupt=False):
            try:
                timed_build()
            except KeyboardInterrupt as e:
                raise e
            except Exception:
                print(traceback.format_exc())
