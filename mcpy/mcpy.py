import contextlib
import contextvars
from dataclasses import dataclass, field
import functools
from typing import IO, Iterator
from pathlib import Path
from collections.abc import Callable

# TODO consider plain class with properties for this
@dataclass
class Context:
    base_dir: Path = Path.cwd()
    namespace_stack: list[str] = field(default_factory=list)
    path_stack: list[str] = field(default_factory=list)
    file_name: str = None
    current_file: IO = None
    file_category: str = None

    def get_namespace(self) -> str:
        return self.namespace_stack[-1]
    
    def get_path(self) -> Path:
        if not self.get_namespace() or not self.file_category:
            raise ValueError('Must set namespace and file category before using path!')

        dir_path = self.base_dir / 'data' / self.get_namespace() / self.file_category / Path('/'.join(self.path_stack))
        return dir_path / self.file_name if self.file_name else dir_path


ctx = contextvars.ContextVar('ctx', default=Context())

@contextlib.contextmanager
def namespace(name):
    ctx.get().namespace_stack.append(name)
    # ctx.get().get_path().mkdir(parents=True, exist_ok=True)
    yield
    ctx.get().namespace_stack.pop()

@contextlib.contextmanager
def dir(name):
    ctx.get().path_stack.append(name)
    # ctx.get().get_path().mkdir(parents=True, exist_ok=True)
    yield
    ctx.get().path_stack.pop()

@contextlib.contextmanager
def mcfunction(name):
    old_file_category: str = ctx.get().file_category
    old_file_name = ctx.get().file_name
    ctx.get().file_name = f'{name}.mcfunction'
    ctx.get().file_category = 'functions'
    full_path = ctx.get().get_path()
    full_path.parent.mkdir(parents=True, exist_ok=True)
    current_file = ctx.get().current_file
    if current_file:
        current_file.close()
    ctx.get().current_file = open(full_path, 'w')
    yield
    ctx.get().current_file.close()
    ctx.get().current_file = None
    ctx.get().file_name = old_file_name
    ctx.get().file_category = old_file_category


def build_datapack(builder_fn: Callable[[],Iterator]):
    cwd = Path.cwd()
    base_dir = None
    if cwd.joinpath('pack.mcmeta').is_file():
        base_dir = cwd
    elif cwd.parent.joinpath('pack.mcmeta').is_file():
        base_dir = cwd.parent
    else:
        raise ValueError('Run inside datapack or datapack/src directory')
    
    print(f'Base dir: {base_dir}')
    ctx.get().base_dir = base_dir
    for item in builder_fn():
        print(f'yielded: {item}')
        if isinstance(item, str):
            ctx.get().current_file.write(item + '\n')
        else:
            raise ValueError(f'Unsupported yield type: {type(item)}')
