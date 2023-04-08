import contextlib
import textwrap
from typing import Iterator
from pathlib import Path
import json
from abc import ABC
from typing import IO, Callable
from pathlib import Path
from dataclasses import dataclass, field

DEFAULT_HEADER_MSG = "Built with mcpy (https://github.com/dthigpen/mcpy)"


@dataclass
class Context:
    base_dir: Path = Path.cwd()
    namespace_stack: list[str] = field(default_factory=list)
    sub_dir_stack: list[Path] = field(default_factory=list)
    file_category: str = None
    file_name: str = None
    opened_file: IO = None
    input_handler: Callable = None


class BasePlugin(ABC):
    def __init__(self, base_dir=None):
        base_dir = Path.cwd() if base_dir is None else Path(base_dir)
        self.ctx = Context(base_dir=base_dir)

    def get_namespace(self) -> str | None:
        """Get the current namespace directory"""
        return (
            self.ctx.namespace_stack[-1] if len(self.ctx.namespace_stack) > 0 else None
        )

    def get_path(self) -> Path:
        """Get the current full path"""
        if not self.ctx.file_category:
            raise ValueError(
                "File category not set! (e.g. pack/data/namespace/<category>/etc)"
            )
        if not self.get_namespace():
            raise ValueError(
                "Namespace not set! (e.g. pack/data/<namespace>/functions/etc)"
            )

        path_dir = (
            self.ctx.base_dir
            / "data"
            / self.get_namespace()
            / Path(self.ctx.file_category).joinpath(*self.ctx.sub_dir_stack)
        )
        if self.ctx.file_name:
            return path_dir / self.ctx.file_name
        return path_dir

    def write(self, item: any):
        """Write the given data to the current file"""
        for handler in self.ctx.write_handlers:
            if handler(self, item):
                break

    def handle_item(self, item: any):
        if not self.ctx.input_handler:
            raise ValueError('Unknown context. Cannot handle input')
        self.ctx.input_handler(item)

    def build(self, items: Iterator | None) -> None:
        if items:
            for item in items:
                self.handle_item(item)


class CorePlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __json_file_handler(self, item: any) -> bool:
        self.__validate_file()
        if self.ctx.file_name.endswith(".json"):
            if isinstance(item, dict):
                item = json.dumps(item, indent=4)

            # lastly, append a newline if its a string
            if isinstance(item, str) and not item.endswith("\n"):
                item += "\n"

            self.ctx.opened_file.write(item)
            return True
        return False

    def __mcfunction_handler(self, item: any) -> bool:
        self.__validate_file()
        if self.ctx.file_name.endswith(".mcfunction"):
            if isinstance(item, list):
                item = "\n".join(item)
            item = textwrap.dedent(item)

            # add trailing newline if not present
            if isinstance(item, str) and not item.endswith("\n"):
                item += "\n"

            self.ctx.opened_file.write(item)
            return True
        return False

    def __validate_file(self) -> None:
        if not self.ctx.opened_file or self.ctx.opened_file.closed:
            raise ValueError("No opened files to write to")
        if not self.ctx.file_name:
            raise ValueError("Cannot write to empty or unspecified file name")

    def __validate_not_in_file_context(self):
        if self.ctx.file_name is not None or self.ctx.opened_file is not None:
            raise ValueError(
                "Illegal state, already in a file context. Try reordering your contexts"
            )

    @contextlib.contextmanager
    def dir(self, name: str):
        self.__validate_not_in_file_context()
        self.ctx.sub_dir_stack.append(Path(name))
        yield
        self.ctx.sub_dir_stack.pop()

    @contextlib.contextmanager
    def namespace(self, name: str):
        self.ctx.namespace_stack.append(name)
        (self.ctx.base_dir / self.get_namespace()).mkdir(parents=True, exist_ok=True)
        yield
        self.ctx.namespace_stack.pop()

    @contextlib.contextmanager
    def file(self, name: str, category=None, mode="w", header=False, *args):
        old_name = self.ctx.file_name
        old_category = self.ctx.file_category
        self.ctx.file_name = name
        self.ctx.file_category = category
        self.get_path().parent.mkdir(parents=True, exist_ok=True)
        with open(self.get_path(), mode, *args) as f:
            self.ctx.opened_file = f
            if header and mode == "w":
                f.write(f"# {DEFAULT_HEADER_MSG}\n\n")
            yield f
        self.ctx.opened_file = None
        self.ctx.file_name = old_name
        self.ctx.file_category = old_category

    @contextlib.contextmanager
    def mcfunction(self, name: str, *args, **kwargs):
        if not name.endswith(".mcfunction"):
            name += ".mcfunction"
        with self.file(name, *args, category="functions", header=True, **kwargs) as f:
            old_handler = self.ctx.input_handler
            self.ctx.input_handler = self.__mcfunction_handler
            yield f
            self.ctx.input_handler = old_handler

    @contextlib.contextmanager
    def json_file(self, name: str, *args, **kwargs):
        if not name.endswith(".json"):
            name += ".json"
        # JSON files can be in multiple file categories so let caller pass it in
        with self.file(name, *args, **kwargs) as f:
            old_handler = self.ctx.input_handler
            self.ctx.input_handler = self.__json_file_handler
            yield f
            self.ctx.input_handler = old_handler

    @contextlib.contextmanager
    def tag(self, name: str, tag_type: str, *args, **kwargs):
        with self.dir(tag_type):
            with self.json_file(name, category="tags", *args, **kwargs) as f:
                yield f

    @contextlib.contextmanager
    def functions(self, name: str, *args, **kwargs):
        with self.tag(name, "functions", *args, **kwargs) as f:
            yield f

    @contextlib.contextmanager
    def blocks(self, name: str, *args, **kwargs):
        with self.tag(name, "blocks", *args, **kwargs) as f:
            yield f

    @contextlib.contextmanager
    def items(self, name: str, *args, **kwargs):
        with self.tag(name, "items", *args, **kwargs) as f:
            yield f
