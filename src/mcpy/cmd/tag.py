from __future__ import annotations
from dataclasses import dataclass
from .util import CmdObject
from .selector import Selector
from collections.abc import Iterator
from ..context import write, get_global_context


def tag_add(entity_selector: Selector, tag: Tag) -> Iterator[str]:
    yield f'tag {entity_selector} add {tag}'

def tag_remove(entity_selector: Selector, tag: Tag) -> Iterator[str]:
    yield f'tag {entity_selector} remove {tag}'

@dataclass
class Tag(CmdObject):
    name: str = None

    def __post_init__(self):
        if self.name is None:
            count = get_global_context().increment_count('tag_count')
            self.name = f'mcpy_tag_{count}'
        super().__post_init__()

    def negate(self) -> Tag:
        return Tag(f'!{self.name}')
    
    def __invert__(self) -> Tag:
        if self.name[0] == '!':
            return Tag(f'{self.name[1:]}')
        return Tag(f'!{self.name}')
    
    def __str__(self):
        return self.name
    
    def add(self, entity_selector: Selector) -> Tag:
        write(tag_add(entity_selector, self))
        return self
    
    def remove(self, entity_selector: Selector) -> Tag:
        write(tag_remove(entity_selector, self))
        return self