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
        # or use built in ones
        s = CurrentEntity.where('tag','foo')
        a = AllPlayers.where('tag','foo')
        r = RandomPlayer.where('tag','foo')
        p = NearestPlayer.where('tag','foo')
        e = Entities.where('tag','foo')
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

AllPlayers = Selector('@a')
CurrentEntity = Selector('@s')
RandomPlayer = Selector('@r')
NearestPlayer = Selector('@p')
Entities = Selector('@e')
