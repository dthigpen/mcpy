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
import tempfile
import shutil

from watchfiles import watch
import dpbuild


def datapack(_func=None, *, include: list[str | Path] = None):
    def decorator_datapack(func):
        @functools.wraps(func)
        def datapack_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        datapack_wrapper.mcpy_datapack = True
        datapack_wrapper.mcpy_include = include if include else []
        return datapack_wrapper

    if _func is None:
        return decorator_datapack
    else:
        return decorator_datapack(_func)


class Datapack:
    def __init__(self, path: str | Path) -> None:
        self.path = valid_datapack_path(path)

    def build(self, changed_files: list[Path]) -> None:
        '''Build the datapack at the current path'''
        pass
    
    def dist(self, output_dir: Path) -> None:
        '''Build this datapack and bundle with dependencies'''
        # TODO this could be copy since there are no deps
        dpbuild.run(self.path,[], output_dir)

class ArchiveDatapack(Datapack):
   def dist(self, output_dir: Path) -> None:
       return shutil.copyfile(self.path, output_dir / self.path.name)
   
   def __init__(self, path: str | Path) -> None:
       self.path = Path(path)


class McpyDatapack(Datapack):
    def __init__(self, path) -> None:
        super().__init__(path)
        valid_mcpy_datapack_path(path)
        self.module = None

    def __get_fn(self) -> Callable:
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
        return marked_functions[0]

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

        build(self.__get_fn(), output_dir)

    def get_includes(self) -> list[str | Path]:
        return getattr(self.__get_fn(), "mcpy_include")

    def dist(self, output_dir: Path):
        if not self.module:
            self.build()
        
        dep_paths: list[Path] = []
        with tempfile.TemporaryDirectory(prefix=f'deps_{self.path.stem}') as tmpdirname:
            tmpdir = Path(tmpdirname)
            for p in self.get_includes():
                p = self.path.parent.resolve() / p
                try:
                    dep_path = valid_mcpy_datapack_path(p)
                    dep_pack = McpyDatapack(p)
                    dep_pack.dist(tmpdir)
                    dep_paths.append(p)
                except Exception as e1:
                    try:
                        dep_path = valid_datapack_path(p)
                        dep_pack = Datapack(p)
                        dep_pack.dist(tmpdir)
                        dep_paths.append(dep_path)
                    except Exception as e2:
                        if p.is_file() and p.suffix == '.zip':
                            dep_pack = ArchiveDatapack(p)
                            dep_pack.dist(tmpdir)
                            dep_paths.append(p)
                        else:
                            print(f'Unknown datapack type at path: {p}')

            dpbuild.run(self.path, dep_paths, output_dir)


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
        list(path.glob("*.py"))
        or list((path / "src").glob("*.py"))
        or list((path / "src").glob("*/*.py"))
    ):
        return path
    raise argparse.ArgumentTypeError(
        f"Datapack does not contain a .py file at {path.name}, {path / 'src'} or {path / 'src' / 'module'}"
    )


def main():
    args = get_args()
    datapack = args.mcpy_datapack

    def timed_build():
        print(f"Building {datapack.path}")
        start = timer()
        datapack.build()
        if args.output_dir:
            datapack.dist(args.output_dir)
        end = timer()
        delta = timedelta(seconds=end - start)
        print(f"Build time: {delta}")

    timed_build()

    if args.watch:
        watch_dirs = [datapack.get_module_path().parent]
        if args.output_dir:
            for p in datapack.get_includes():
                p = datapack.path.parent.resolve() / p
                try:
                    dep_pack = McpyDatapack(p)
                    watch_dirs.append(dep_pack.get_module_path().parent)
                except:
                    try:
                        dep_pack = valid_datapack_path(p)
                        watch_dirs.append(dep_pack)
                    except:
                        pass
        print(f"Watching files")
        print("Press Ctrl-C to stop at anytime")
        for _ in watch(*watch_dirs, raise_interrupt=False):
            try:
                timed_build()
            except KeyboardInterrupt as e:
                raise e
            except Exception:
                print(traceback.format_exc())
