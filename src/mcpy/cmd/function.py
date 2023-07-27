from dataclasses import dataclass
from .util import CmdObject

@dataclass
class Function(CmdObject):
    '''A container for mcfunction resources. E.g. namespace:path/to/mcfunction
    '''
    resource_location: str

    def __str__(self) -> str:
        return self.resource_location
    
class Fn(Function):
    pass


def function(function_resource_path: str):
    '''Function command'''
    yield f'function {function_resource_path}'

