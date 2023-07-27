from abc import ABC, abstractmethod
from dataclasses import dataclass
from .util import tokens_to_str


@dataclass
class Pos:
    '''A container for x y z position data
    '''
    x: str
    y: str
    z: str

    def __str__(self) -> str:
        return tokens_to_str(self.x, self.y, self.z)

@dataclass
class CmdObject:
    
    def __post_init__(self):
        if not self.validate():
            raise TypeError('Invalid arguments')
    
    def validate(self):
        return True

    @abstractmethod
    def __str__(self) -> str:
        pass

