import contextlib
import textwrap
from typing import IO, Iterator
from pathlib import Path
import json


class Datapack:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.namespace_stack: list[str] = []
        self.sub_dir_stack: list[Path] = []
        self.file_category: str = None
        self.file_name: str = None
        self.opened_file: IO = None
        self.write_handlers = []
        self.write_handlers.append(Datapack.__mcfunction_handler)
        self.write_handlers.append(Datapack.__json_file_handler)

    def get_namespace(self) -> str | None:
        """Get the current namespace directory"""
        return self.namespace_stack[-1] if len(self.namespace_stack) > 0 else None

    def get_path(self) -> Path:
        """Get the current full path"""
        if not self.file_category:
            raise ValueError(
                "File category not set! (e.g. pack/data/namespace/<category>/etc)"
            )
        if not self.get_namespace():
            raise ValueError(
                "Namespace not set! (e.g. pack/data/<namespace>/functions/etc)"
            )

        path_dir = (
            self.base_dir
            / "data"
            / self.get_namespace()
            / Path(self.file_category).joinpath(*self.sub_dir_stack)
        )
        if self.file_name:
            return path_dir / self.file_name
        return path_dir

    def __json_file_handler(self, item: any) -> bool:
        self.__validate_file()
        if self.file_name.endswith(".json"):
            if isinstance(item, dict):
                item = json.dumps(item, indent=4)

            # lastly, append a newline if its a string
            if isinstance(item, str) and not item.endswith("\n"):
                item += "\n"

            self.opened_file.write(item)
            return True
        return False

    def __mcfunction_handler(self, item: any) -> bool:
        self.__validate_file()
        if self.file_name.endswith(".mcfunction"):
            if isinstance(item, list):
                item = "\n".join(item)
                valid = True
            # TODO fix multiline string indent issue
            item = textwrap.dedent(item)

            # add trailing newline if not present
            if isinstance(item, str) and not item.endswith("\n"):
                item += "\n"

            self.opened_file.write(item)
            return True
        return False

    def __validate_file(self) -> None:
        if not self.opened_file or self.opened_file.closed:
            raise ValueError("No opened files to write to")
        if not self.file_name:
            raise ValueError("Cannot write to empty or unspecified file name")

    def write(self, item: any):
        """Write the given data to the current file"""
        for handler in self.write_handlers:
            if handler(self, item):
                break

    def build(self, items: Iterator | None) -> None:
        if items:
            for item in items:
                self.write(item)

    @contextlib.contextmanager
    def dir(self, name: str):
        self.sub_dir_stack.append(Path(name))
        yield
        self.sub_dir_stack.pop()

    @contextlib.contextmanager
    def namespace(self, name: str):
        self.namespace_stack.append(name)
        (self.base_dir / self.get_namespace()).mkdir(parents=True, exist_ok=True)
        yield
        self.namespace_stack.pop()

    @contextlib.contextmanager
    def file(self, name: str, category=None, mode="w", *args):
        old_name = self.file_name
        old_category = self.file_category
        self.file_name = name
        self.file_category = category
        self.get_path().parent.mkdir(parents=True, exist_ok=True)
        with open(self.get_path(), mode, *args) as f:
            self.opened_file = f
            yield f
        self.opened_file = None
        self.file_name = old_name
        self.file_category = old_category

    @contextlib.contextmanager
    def mcfunction(self, name: str, *args, **kwargs):
        if not name.endswith(".mcfunction"):
            name += ".mcfunction"
        with self.file(name, *args, category="functions", **kwargs) as f:
            yield f

    @contextlib.contextmanager
    def json_file(self, name: str, *args, **kwargs):
        if not name.endswith(".json"):
            name += ".json"
        # JSON files can be in multiple file categories so let caller pass it in
        with self.file(name, *args, **kwargs) as f:
            yield f
