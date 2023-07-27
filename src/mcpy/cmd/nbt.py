from dataclasses import dataclass, replace
from .common import CmdObject
from typing import Union

NbtPrimitive = Union[str, int, bool, dict, list]

@dataclass
class Value(CmdObject):
    '''NBT Value base class'''
    value: any

    def __str__(self):
        return str(self.value)

    
@dataclass
class Str(Value):
    '''A container for string values'''
    value: str
    
    def __str__(self) -> str:
        escaped = self.value.replace('"','\\"')
        return f'"{escaped}"'

@dataclass
class Byte(Value):
    '''NBT Byte container'''
    value: int

    def __str__(self) -> str:
        return f'{self.value}b'

@dataclass
class Float(Value):
    '''NBT Float container'''
    value: int

    def __str__(self) -> str:
        return f'{self.value}f'

@dataclass
class Short(Value):
    '''NBT Short container'''
    value: int

    def __str__(self) -> str:
        return f'{self.value}s'


@dataclass
class Bool(Value):
    '''NBT Bool container'''
    value: bool
    def __str__(self) -> str:
        return 'true' if self.value is True else 'false'
    
@dataclass
class Int(Value):
    '''NBT Int container'''
    value: int

    def __str__(self) -> str:
        return f'{self.value}'


@dataclass
class NbtObj(Value):
    '''NBT Compound container'''
    value: dict

    def __str__(self):
        res = '{'
        for idx, (key, val) in enumerate(self.value.items()):
            res += f'"{key}": {as_nbt(val)}'
            if idx < len(self.value) - 1:
                res += ', '
        res += '}'
        return res


@dataclass
class NbtList(Value):
    '''NBT List container'''
    value: list

    def __str__(self):
        res = '['
        for idx, val in enumerate(self.value):
            
            res += f'{as_nbt(val)}'
            if idx < len(self.value) - 1:
                res += ', '
        res += ']'
        return res


@dataclass
class NbtPath(CmdObject):
    '''NBT Path container'''
    _path: str

    def __str__(self):
        return self._path
    
    def key(self, subpath: str):
        return replace(self, _path=f'{self._path}.{subpath}')
    
    def at(self, index: any):
        return replace(self, _path=f'{self._path}[{index}]')


def as_nbt(primitive_value: any):
    '''Convert the given type into its NBT wrapped type if possible'''
    if isinstance(primitive_value, Value):
        return primitive_value
    elif isinstance(primitive_value, str):
        return Str(primitive_value)
    elif isinstance(primitive_value, bool):
        return Bool(primitive_value)
    elif isinstance(primitive_value, int):
        return Int(primitive_value)
    elif isinstance(primitive_value, dict):
        return NbtObj(primitive_value)
    elif isinstance(primitive_value, list):
        return NbtList(primitive_value)
    else:
        raise ValueError(f'Value cannot be converted into NBT: {primitive_value}')

