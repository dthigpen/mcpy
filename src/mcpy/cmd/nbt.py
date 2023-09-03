'''
Module for all NBT related container types and functions.
Not all of these NBT container types need to be constructed on their own because most functions that use them as parameters can convert their primitive types directly. (e.g. a `dict` can be used instead of constructing an `NbtObj`)

Attributes:
    NbtPrimitive (Union[str, int, bool, dict, list]): Data types that can be converted into valid NBT data
'''
from __future__ import annotations
from dataclasses import dataclass, replace
from .block import CmdObject
from typing import Union
from typing_extensions import Self
NbtPrimitive = Union[str, int, bool, dict, list]

@dataclass
class Value(CmdObject):
    '''Base container type for all NBT value types.
    Can also be used to express any string-able value.

    Attributes:
        value: Raw value. String representation will be used in commands.

    Example:
        ``` python
        macro_value = Value('$(my_macro_var)')
        ```
    '''

    value: any

    def __str__(self):
        return str(self.value)

    
@dataclass
class Str(Value):
    '''Container type for string values
    
    Attributes:
        value: String value. Double quotes will be escaped when used in commands
    
    Example:
        ``` python
        value = Str('Some name')
        ```
    '''
    value: str
    
    def __str__(self) -> str:
        escaped = self.value.replace('"','\\"')
        return f'"{escaped}"'

@dataclass
class Byte(Value):
    '''Container type for NBT Byte values.

    Attributes:
        value: Int representation of bytes
    
    Example:
        ``` python
        value = Byte(12)
        ```
    '''
    value: int

    def __str__(self) -> str:
        return f'{self.value}b'

@dataclass
class Float(Value):
    '''Container type for NBT Float values.

    Attributes:
        value: Float
    
    Example:
        ``` python
        value = Float(12.3)
        ```
    '''
    value: float

    def __str__(self) -> str:
        return f'{self.value}f'

@dataclass
class Short(Value):
    '''Container type for NBT Short values.

    Attributes:
        value: Int representation of short
    
    Example:
        ``` python
        value = Short(12)
        ```
    '''
    value: int

    def __str__(self) -> str:
        return f'{self.value}s'


@dataclass
class Bool(Value):
    '''Container type for NBT Boolean values.

    Attributes:
        value: Bool
    
    Example:
        ``` python
        value = Bool(True)
        ```
    '''
    value: bool
    def __str__(self) -> str:
        return 'true' if self.value is True else 'false'
    
@dataclass
class Int(Value):
    '''Container type for NBT Int values.

    Attributes:
        value: Int

    Example:
        ``` python
        value = Int(12)
        ```
    '''
    value: int

    def __str__(self) -> str:
        return f'{self.value}'


@dataclass
class NbtObj(Value):
    '''Container type for NBT Compound values. (e.i. JSON object)

    Attributes:
        value: Dict representation of object

    Example:
        ``` python
        value = NbtObj({'name':'Some name'})
        ```
    '''
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
    '''Container type for NBT List values.

    Attributes:
        value: List
    
    Example:
        ``` python
        value = NbtList(['foo','bar'])
        ```
    '''
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
    '''Container type for NBT paths
    
    Attributes:
        path: String data path (e.g. Inventory[0])
    
    Example:
        ``` python
        value = NbtPath('some.nested.path')
        ```
    '''
    path: str

    def __str__(self):
        return self.path
    
    def __getitem__(self, key: any) -> NbtPath:
        if isinstance(key, str):
            return self.key(key)
        elif isinstance(dict, key):
            return self.where(key)

    def key(self, subpath: str) -> Self:
        '''Create a new path from the current and given subpath
        Attributes:
            subpath: Subpath key(s) to add to this path
        Returns:
            A new NbtPath
        '''
        return replace(self, path=f'{self.path}.{subpath}')
    
    def where(self, index_or_query: any):
        '''Create a new path from the current and given index or query
        Attributes:
            index_or_query: Index or query
        Returns:
            A new NbtPath
        '''
        index_or_query = as_nbt(index_or_query)
        return replace(self, path=f'{self.path}[{index_or_query}]')
    
    def at(self, index: any):
        '''Create a new path from the current and given index or query
        Attributes:
            index_or_query: Index or query
        Returns:
            A new NbtPath
        '''
        return self.where(index)


def as_nbt(primitive_value: any):
    '''Convert the given type into its NBT wrapped type if possible
    
    Attributes:
        primitive_value: value
    
    Returns:
        NBT subtype that corresponds to the given Python type value

    Raises:
        ValueError: When a NBT type is not found for the given value
    '''
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

