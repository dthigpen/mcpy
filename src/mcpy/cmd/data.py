from .nbt import Value, NbtPath, as_nbt, NbtPrimitive
from .util import tokens_to_str
from dataclasses import dataclass
from .nbt import Value, NbtPrimitive
from typing import Union


@dataclass
class StoragePath(NbtPath):
    '''A container for a storage path'''
    _namespace: str
    
    def __str__(self):
        return tokens_to_str(self._namespace, self._path)

@dataclass
class EntityPath(NbtPath):
    '''A container for an entity path'''
    _selector: str
    def __str__(self):
        return tokens_to_str(self._selector, self._path)

@dataclass
class BlockPath(NbtPath):
    '''A container for a block path'''
    _pos: str

    def __str__(self):
        return tokens_to_str(self._pos, self._path)

TargetType = Union[StoragePath, EntityPath, BlockPath]
SourceType = Union[StoragePath, EntityPath, BlockPath, Value, NbtPrimitive]

def get_target_type(target: TargetType | Value):
    '''Gets the string representation of the class type to be used in commands'''
    if isinstance(target, EntityPath):
        return 'entity'
    elif isinstance(target, StoragePath):
        return 'storage'
    elif isinstance(target, BlockPath):
        return 'block'
    elif isinstance(target, Value):
        return 'value'
    raise ValueError(f'Unsupported target type: {type(target)}')
        

def modify_set(target: TargetType, source: SourceType):
    '''Sets the target path to the given source path or value
    
    Args:
        target: target path
        source: source path or value

    Returns:
        yielded command
    '''
    target_type = get_target_type(target)
    source = __wrap_source_type(source)
    source_type = get_target_type(source)
    if source_type != 'value':
        source_type = 'from ' + source_type

    yield f'data modify {target_type} {target} set {source_type} {source}'


def modify_append(target: TargetType, source: SourceType):
    '''Appends the source path or value to the given target path
    
    Args:
        target: target path
        source: source path or value

    Returns:
        yielded command
    '''
    target_type = get_target_type(target)
    source = __wrap_source_type(source)
    source_type = get_target_type(source)
    if source_type != 'value':
        source_type = 'from ' + source_type
    yield f'data modify {target_type} {target} append {source_type} {source}'

def remove(target: TargetType):
    '''Remove the target path
    
    Args:
        target: target path

    Returns:
        yielded command
    '''
    yield f'data modify {get_target_type(target)} {target}'

def __wrap_source_type(source: SourceType) -> TargetType | Value:
    if isinstance(source, (Value, StoragePath, EntityPath, BlockPath)):
        return source
    source = as_nbt(source)
    return source
