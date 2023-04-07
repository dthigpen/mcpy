import contextlib
import textwrap
from typing import IO, Iterator
from pathlib import Path


class Datapack:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.namespace_stack: list[str] = []
        self.sub_dir_stack: list[Path] = []
        self.file_category: str = None
        self.file_name: str = None
        self.opened_file: IO = None

    def get_namespace(self) -> str | None:
        return self.namespace_stack[-1] if len(self.namespace_stack) > 0 else None

    def get_path(self) -> Path:
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

    def write_line(self, line: str | list[str]):
        if not self.opened_file or self.opened_file.closed:
            raise ValueError("No opened files to write to")
        if isinstance(line, list):
            line = "\n".join(line)
        if not line.endswith("\n"):
            line += "\n"
        # TODO fix multiline string indent issue
        line = textwrap.dedent(line)
        self.opened_file.write(line)

    def build(self, items: Iterator | None) -> None:
        if items:
            for item in items:
                if isinstance(item, str) or isinstance(item, list):
                    self.write_line(item)
                else:
                    raise ValueError(
                        f"Unsupported yield type: {type(item)} value: {item}"
                    )

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
    def mcfunction(self, name: str, *args):
        if not name.endswith(".mcfunction"):
            name += ".mcfunction"
        with self.file(name, category="functions", *args) as f:
            yield f
