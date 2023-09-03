'''
Module for all tag command container types and functions
'''
from __future__ import annotations
from dataclasses import dataclass
from .util import CmdObject
from .selector import Selector
from collections.abc import Iterator
from ..context import write, get_global_context


def tag_add(entity_selector: Selector, tag: Tag) -> Iterator[str]:
    '''Command template function to add a tag to the given selector

    Args:
        entity_selector: Entity to add the tag to
        tag: tag to add
    
    Returns:
        yielded command

    Example:
        ``` python
        enabled = Tag('enabled')
        tag_add(CurrentEntity(), enabled)
        tag_add(CurrentEntity(), 'foo')
        ```
    '''
    yield f'tag {entity_selector} add {tag}'

def tag_remove(entity_selector: Selector, tag: Tag) -> Iterator[str]:
    '''Command template function to remove a tag to the given selector

    Args:
        entity_selector: Entity to remove the tag to
        tag: tag to remove
    
    Returns:
        yielded command

    Example:
        ``` python
        enabled = Tag('enabled')
        tag_remove(CurrentEntity(), enabled)
        tag_remove(CurrentEntity(), 'foo')
        ```
    '''
    yield f'tag {entity_selector} remove {tag}'

@dataclass
class Tag(CmdObject):
    '''Command template function to add a tag to the given selector

    Attributes:
        name: Optional name for the tag
    
    Example:
        ``` python
        enabled = Tag('enabled')
        temp_tag = Tag()
        ```
    '''
    name: str = None

    def __post_init__(self):
        if self.name is None:
            count = get_global_context().increment_count('tag_count')
            self.name = f'mcpy_tag_{count}'
        super().__post_init__()

    def negate(self) -> Tag:
        '''Negates this tag by prefixing a `!`.

        Returns:
            New negated tag
        
        Example:
            ``` python
            enabled = Tag('enabled')
            not_enabled = Entities().where('tag', enabled.negate())
            ```
        '''
        if self.name[0] == '!':
            return Tag(f'{self.name[1:]}')
        return Tag(f'!{self.name}')
    
    def __invert__(self) -> Tag:
        '''Operator to negate a tag. See `Tag.negate`

        Returns:
            New negated tag

        Example:
            ``` python
            enabled = Tag('enabled')
            not_enabled = Entities().where('tag', ~enabled)
            ```
        '''
        return self.negate()
    
    def __str__(self):
        return self.name
    
    def add(self, entity_selector: Selector) -> Tag:
        '''Add this tag to the given entity

        Args:
            entity_selector: Entity to add this tag to
        Returns:
            Self

        Example:
            ``` python
            enabled = Tag('enabled')
            enabled.add(CurrentEntity())
            ```
        '''
        write(tag_add(entity_selector, self))
        return self
    
    def remove(self, entity_selector: Selector) -> Tag:
        '''Remove this tag from the given entity

        Args:
            entity_selector: Entity to remove this tag from
        Returns:
            Self

        Example:
            ``` python
            enabled = Tag('enabled')
            enabled.remove(CurrentEntity())
            ```
        '''
        write(tag_remove(entity_selector, self))
        return self