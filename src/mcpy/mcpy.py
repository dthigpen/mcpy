import argparse
import importlib
from typing import Callable
from types import ModuleType
from pathlib import Path
from timeit import default_timer as timer
import traceback
from datetime import timedelta
from .context import Context, write, init_context
import functools
import json
import tempfile
import shutil
import re
from string import Template

from .config import (
    load_config,
    load_default_config,
    write_config,
    load_config_for_datapack,
    find_config_path,
    DEFAULT_CONFIG,
    DEFAULT_NAME,
)

from watchfiles import watch
import dpbuild


def datapack(_func=None, *, include: list[str | Path] = None):
    '''Decorator to wrap a datapack creation function

    Args:
        include: The names of dependencies to bundle this datapack with

    '''
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


class _Datapack:
    '''Class to represent a datapack on the filesystem'''
    def __init__(self, path: str | Path) -> None:
        self.path = _valid_datapack_path(path)

    def build(self, changed_files: list[Path]) -> None:
        """Build the datapack at the current path"""
        pass

    def bundle(self, output_dir: Path) -> None:
        """Build this datapack and bundle with dependencies"""
        # TODO this could be copy since there are no deps
        dpbuild.run(self.path, [], output_dir)


class _ArchiveDatapack(_Datapack):
   '''Class to represent a compressed datapack'''
   def bundle(self, output_dir: Path) -> None:
       return shutil.copyfile(self.path, output_dir / self.path.name)
   
   def __init__(self, path: str | Path) -> None:
       self.path = Path(path)


class _McpyDatapack(_Datapack):
    '''Class to represent an Mcpy datapack'''
    def __init__(self, path) -> None:
        super().__init__(path)
        _valid_mcpy_datapack_path(path)
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

    def load_config(self) -> dict:
        '''Get the config file for this datapack
        
        Returns
            A dict of the config keys and values
        
        '''
        return load_config_for_datapack(self.path)

    def get_module_path(self) -> Path:
        '''Get the path to this datapack's python module (e.g. pack.py)'''
        config = self.load_config()
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
        '''Update the datapack's data directory by running its code'''
        if not output_dir:
            output_dir = self.path
        if not self.module:
            module_path = self.get_module_path()
            module_name = str(module_path.parent / module_path.stem).replace("/", ".")
            self.module = importlib.import_module(module_name)
        else:
            self.module = importlib.reload(self.module)

        build(self.__get_fn(), output_dir, config=self.load_config())

    def get_includes(self) -> list[str | Path]:
        '''Get the list of dependency paths to be included in the bundled datapack
        
        Returns:
            A list of dependency paths relative to the datapack's root
            
        '''
        return getattr(self.__get_fn(), "mcpy_include")

    def bundle(self, output_dir: Path):
        '''Bundle the datapack and dependencies to an output directory'''
        if not self.module:
            self.build()

        dep_paths: list[Path] = []
        with tempfile.TemporaryDirectory(prefix=f"deps_{self.path.stem}") as tmpdirname:
            tmpdir = Path(tmpdirname)
            for p in self.get_includes():

                p = self.path.resolve().parent.resolve() / p
                try:
                    dep_path = _valid_mcpy_datapack_path(p)
                    dep_pack = _McpyDatapack(p)
                    dep_pack.bundle(tmpdir)
                    dep_paths.append(p)
                except Exception as e1:
                    try:
                        dep_path = _valid_datapack_path(p)
                        dep_pack = _Datapack(p)
                        dep_pack.bundle(tmpdir)
                        dep_paths.append(dep_path)
                    except Exception as e2:
                        if p.is_file() and p.suffix == ".zip":
                            dep_pack = _ArchiveDatapack(p)
                            dep_pack.bundle(tmpdir)
                            dep_paths.append(p)
                        else:
                            print(f"Unknown datapack type at path: {p}")

            dpbuild.run(self.path, dep_paths, output_dir)


def __get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build mcpy datapacks!")
    subparsers = parser.add_subparsers(dest="command")
    init_parser = subparsers.add_parser("init")
    # TODO type dir not just path
    init_parser.add_argument("dir", nargs="?", type=Path, default=".", help="Directory")
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument(
        "mcpy_datapack",
        nargs="?",
        type=_McpyDatapack,
        default=".",
        help="mcpy datapack directory",
    )
    build_parser.add_argument(
        "-w", "--watch", action="store_true", help="watch file changes and rebuild"
    )
    build_parser.add_argument(
        "-o", "--output-dir", type=Path, help="Directory to put compiled datapack"
    )
    args = parser.parse_args()
    sub_commands = ('init', 'build')
    if args.command not in sub_commands:
        print(f'Must specify a valid command: {", ".join(sub_commands)}')
        print(f'See help command for details.')
        exit(1)
    return args


def build(builder_fn: Callable[[Context], None], output_dir: Path, config=None):
    '''Calls the given datapack builder function and writes the datapack to the output directory
    
    This automatically gets called when using the CLI tool.
    
    Args:
        builder_fn: The datapack builder function
        output_dir: The output location of the datapack
    
    '''
    if config is None:
        config = load_default_config()
    with init_context(output_dir, config):
        items = builder_fn()
        if items:
            for item in items:
                write(item)


def _valid_datapack_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"Path to datapack does not exist: {path}")

    mc_meta_file = path / "pack.mcmeta"
    if not mc_meta_file.is_file():
        raise argparse.ArgumentTypeError(
            f"Datapack does not have a pack.mcmeta file: {mc_meta_file}"
        )

    return path


def _valid_mcpy_datapack_path(path_str: str) -> Path:
    path = _valid_datapack_path(path_str)

    if (
        list(path.glob("*.py"))
        or list((path / "src").glob("*.py"))
        or list((path / "src").glob("*/*.py"))
    ):
        return path
    raise argparse.ArgumentTypeError(
        f"Datapack does not contain a .py file at {path.name}, {path / 'src'} or {path / 'src' / 'module'}"
    )


def init_project(datapack_path: Path):
    def input_value(name: str, default: str = None) -> str:
        prompt = f"{name}: "
        if default:
            prompt += f"({default}) "
        res = input(prompt)
        return res if res.strip() else default

    def confirm(text: str) -> bool:
        res = input(f"{text}[y/n] ").strip().lower()
        return res in ["y", "yes"]

    if not datapack_path.is_dir():
        if confirm(f"Create datapack dir at {datapack_path}? "):
            datapack_path.mkdir(exist_ok=True, parents=True)
        else:
            return
    mc_meta = datapack_path / "pack.mcmeta"
    if not mc_meta.is_file():
        desc = input_value("description", default="")
        version = input_value("pack_format", default=15)
        obj = {"version": version, "description": desc}
        mc_meta.write_text(json.dumps(obj, indent=True))

    # used for hello world
    default_namespace = re.sub(r"[^a-z0-9_.\-]", "", datapack_path.resolve().stem.lower())
    pack_namespace = input_value("Datapack namespace", default=default_namespace)
    # TODO write hello world pack.py and build once?

    src_path = datapack_path / "src"
    src_path.mkdir(parents=True, exist_ok=True)
    pack_file_name = input_value("entrypoint file", default="pack.py")
    pack_file_path = src_path / pack_file_name
    config_path = find_config_path(datapack_path, use_default=True)
    config = load_config(config_path, nonexistent_ok=True)
    do_write_config = False

    # add override to config
    if pack_file_name != "pack.py":
        do_write_config = True
        config["entrypoint"] = pack_file_name

    # ask if want config only if not already writing
    if do_write_config:
        write_config(config_path, config)
    else:
        if confirm("Create config file? (mcpy_config.json) "):
            write_config(config_path, config)

    if pack_file_path.is_file():
        print(f"Pack file exists at {pack_file_path}, will not write sample mcpy file.")
    else:
        default_program = Template(
            """\
from mcpy import *

@datapack
def simple_pack():
    with namespace("$datapack_namespace"):
        with dir("api/greetings"):
            with mcfunction("hello"):
                yield "say Hello!"

    with namespace("minecraft"):
        with functions("load"):
            yield {"values": ["$datapack_namespace:api/greetings/hello"]}
"""
        ).safe_substitute({"datapack_namespace": pack_namespace})
        pack_file_path.write_text(default_program)


def _main():
    args = __get_args()
    if args.command == "init":
        init_project(args.dir)
        return
    

    datapack: _Datapack = args.mcpy_datapack

    def timed_build():
        print(f"Building {datapack.path}")
        start = timer()
        datapack.build()
        if args.output_dir:
            datapack.bundle(args.output_dir)
        end = timer()
        delta = timedelta(seconds=end - start)
        print(f"Build time: {delta}")

    timed_build()

    if args.watch:
        watch_dirs = [datapack.get_module_path().parent]
        if args.output_dir:
            for p in datapack.get_includes():
                p = datapack.path.resolve().parent.resolve() / p
                try:
                    dep_pack = _McpyDatapack(p)
                    watch_dirs.append(dep_pack.get_module_path().parent)
                except:
                    try:
                        dep_pack = _valid_datapack_path(p)
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
