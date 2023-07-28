from __future__ import annotations
from dataclasses import dataclass
from .util import tokens_to_str, CmdObject


@dataclass
class Pos(CmdObject):
    '''A container for x y z position data
    '''
    x: str
    y: str
    z: str

    def __str__(self) -> str:
        return tokens_to_str(self.x, self.y, self.z)
