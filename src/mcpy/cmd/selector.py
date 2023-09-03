'''
Module for all entity selector container types and functions
'''

from __future__ import annotations
from dataclasses import dataclass, field
from .util import CmdObject
from .data import EntityPath
@dataclass
class Selector(CmdObject):
    '''Base container type for entity selectors
    
    Attributes:
        entity_type: type of entity (e.g. @s, @p)
        arguments: selector arguments built with `where` function

    Example:
        ``` python
        s = Selector('@s').where('tag','foo')
        ```
    '''
    entity_type: str
    arguments: tuple = field(default_factory=tuple)

    def where(self, arg: str, value: any) -> Selector:
        return Selector(self.entity_type, (*self.arguments, (arg, value)))
    
    def to_path(self, starting_path: str) -> EntityPath:
        return EntityPath(starting_path, str(self))
    
    def __str__(self) -> str:
        result = self.entity_type
        if self.arguments:
            result += '['
            def key_equal_value_str(data: list | tuple) -> str:
                arg_strs = []

                for key,value in data:
                    val_str=str(value)
                    if isinstance(value, (dict, tuple, list)):
                        kv_list = [(k,v) for k,v in value.items()]
                        val_str = '{' + key_equal_value_str(kv_list) + '}'
                    arg_strs.append(f'{key}={val_str}')   
                return ','.join(arg_strs)
            result += key_equal_value_str(self.arguments)
            result += ']'
        return result


class AllPlayers(Selector):
    '''`@a` selector container type
    
    Example:
        ``` python
        s = AllPlayers().where('tag','foo')
        ```
    '''
    def __init__(self):
        super().__init__('@a')

class RandomPlayer(Selector):
    '''`@r` selector container type
    
    Example:
        ``` python
        s = RandomPlayer().where('tag','foo')
        ```
    '''
    def __init__(self):
        super().__init__('@r')

class NearestPlayer(Selector):
    '''`@p` selector container type
    
    Example:
        ``` python
        s = NearestPlayer().where('tag','foo')
        ```
    '''
    def __init__(self):
        super().__init__('@p')

class CurrentEntity(Selector):
    '''`@s` selector container type
    
    Example:
        ``` python
        s = CurrentEntity().where('tag','foo')
        ```
    '''
    def __init__(self):
        super().__init__('@s')

class AllEntities(Selector):
    '''`@e` selector container type
    
    Example:
        ``` python
        s = AllEntities().where('tag','foo')
        ```
    '''
    def __init__(self):
        super().__init__('@e')

class Entities(AllEntities):
    '''`@e` selector container type
    
    Example:
        ``` python
        s = Entities().where('tag','foo')
        ```
    '''
    pass

