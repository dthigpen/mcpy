from dataclasses import dataclass, asdict
from .util import tokens_to_str


@dataclass
class Player:
    name: str
    objective: str


# @dataclass
# class __Target:
#     target: str
#     target_path: str = None


@dataclass
class Storage:
    target: str
    target_path: str = None


@dataclass
class Entity:
    target: str
    target_path: str = None


@dataclass
class Pos:
    x: str
    y: str
    z: str

    def __str__(self) -> str:
        return tokens_to_str(self.x, self.y, self.z)


@dataclass
class Block:
    pos: Pos | str
    target_path: str = None
