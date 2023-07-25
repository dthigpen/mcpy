from __future__ import annotations
import contextlib
from dataclasses import dataclass

from ..context import write, get_global_context
from .scoreboard import Score, get
from .data import StoragePath, EntityPath, BlockPath, modify_set, modify_append, remove
from .nbt import Value, NbtPrimitive
from typing import Union

TargetType = Union[StoragePath, EntityPath, BlockPath]
SourceType = Union[StoragePath, EntityPath, BlockPath, Value, NbtPrimitive]


@contextlib.contextmanager
def scope():
    write('function call_stack:push')
    yield
    write('function call_stack:pop')

CALL_STACK_NAMESPACE = 'call_stack:'

class Var(StoragePath):
    '''Storage based container for scoped variable data'''
    def __init__(self, name: str = None):
        if name is None:
            name = get_global_context().counter['var_count']
            get_global_context().counter['var_count'] += 1
            name = f'this.var{name}'
        super().__init__(name, CALL_STACK_NAMESPACE)


    def set(self, value: TargetType) -> Var:
        '''Set the variable to the given value'''
        write(modify_set(self, value))
        return self
    
    def set_from_score(self, score: Score, result_type: str='int', scale=1) -> Var:
        '''Set the variable to the stored result of the given score'''
        write(f'execute store result storage {self} {result_type} {scale} run {get(score)}')
        
    def append(self, value: TargetType) -> Var:
        '''Append a value to this variable'''
        write(modify_append(self, value))
        return self

    def copy(self, name=None) -> Var:
        '''Copy this variable to a new variable'''
        return Var(name=name)
    
    def remove(self):
        '''Remove this variable from storage'''
        remove(self)
