from .nbt import Value, NbtPath, as_nbt, NbtPrimitive
from .util import tokens_to_str
from dataclasses import dataclass, field
from .nbt import Value, NbtPrimitive
from typing import Union, Iterator
from .scoreboard import Score, score_get
from .exec import execute
from ..context import write
from .tellraw import Tellable


@dataclass
class DataCondition:
    def present(self) -> str:
        return f"data {get_target_type(self)} {self}"

    # TODO has_value condition
    def has_value(self) -> str:
        raise NotImplementedError()


@dataclass
class DataPath(NbtPath, DataCondition):
    def to_score(self, holder=None, objective=None) -> Score:
        score = Score(holder=holder, objective=objective)
        with execute(f"store result score {score}"):
            write(data_get(self))
        return score

    def set(self, value: any):
        """Set the variable to the given value"""
        write(data_modify_set(self, value))
        return self

    def set_from_score(self, score: Score, result_type: str = "int", scale=1):
        """Set the variable to the stored result of the given score"""
        write(
            f"execute store result storage {self} {result_type} {scale} run {score_get(score)}"
        )

    def merge(self, source: any, modify=True):
        if modify:
            write(data_modify_merge(self, source))
        else:
            write(data_merge(self, source))
        return self

    def append(self, value: any):
        """Append a value to this variable"""
        write(data_modify_append(self, value))
        return self

    def remove(self):
        """Remove this variable from storage"""
        write(data_remove(self))
        return self


@dataclass
class StoragePath(DataPath, Tellable):
    """A container for a storage path"""

    namespace: str

    def to_tellable(self) -> dict:
        return {"nbt": self.path, get_target_type(self): self.namespace}

    def __str__(self):
        return tokens_to_str(self.namespace, self.path)


@dataclass
class EntityPath(DataPath, Tellable):
    """A container for an entity path"""

    selector: str

    def to_tellable(self) -> dict:
        return {"nbt": self.path, get_target_type(self): self.selector}

    def __str__(self):
        return tokens_to_str(self.selector, self.path)


@dataclass
class BlockPath(DataPath, Tellable):
    """A container for a block path"""

    pos: str

    def to_tellable(self) -> dict:
        return {"nbt": self.path, get_target_type(self): self.pos}
    
    def __str__(self):
        return tokens_to_str(self.pos, self.path)


TargetType = Union[StoragePath, EntityPath, BlockPath]
SourceType = Union[StoragePath, EntityPath, BlockPath, Value, NbtPrimitive]


def get_target_type(target: TargetType | Value):
    """Gets the string representation of the class type to be used in commands"""
    if isinstance(target, EntityPath):
        return "entity"
    elif isinstance(target, StoragePath):
        return "storage"
    elif isinstance(target, BlockPath):
        return "block"
    elif isinstance(target, Value):
        return "value"
    raise ValueError(f"Unsupported target type: {type(target)}")


def data_get(target: TargetType):
    target_type = get_target_type(target)
    yield f"data get {target_type} {target}"


def data_modify_set(target: TargetType, source: SourceType)-> Iterator[str]:
    """Sets the target path to the given source path or value

    Args:
        target: target path
        source: source path or value

    Returns:
        yielded command
    """
    target_type = get_target_type(target)
    source = __wrap_source_type(source)
    source_type = get_target_type(source)
    if source_type != "value":
        source_type = "from " + source_type

    yield f"data modify {target_type} {target} set {source_type} {source}"


def data_modify_append(target: TargetType, source: SourceType) -> Iterator[str]:
    """Appends the source path or value to the given target path

    Args:
        target: target path
        source: source path or value

    Returns:
        yielded command
    """
    target_type = get_target_type(target)
    source = __wrap_source_type(source)
    source_type = get_target_type(source)
    if source_type != "value":
        source_type = "from " + source_type
    yield f"data modify {target_type} {target} append {source_type} {source}"


def data_modify_merge(target: TargetType, source: SourceType):
    target_type = get_target_type(target)
    source = __wrap_source_type(source)
    source_type = get_target_type(source)
    if source_type != "value":
        source_type = "from " + source_type
    yield f"data modify {target_type} {target} merge {source_type} {source}"


def data_merge(target: TargetType, source: Value):
    raise NotImplementedError()


def data_remove(target: TargetType)-> Iterator[str]:
    """Remove the target path

    Args:
        target: target path

    Returns:
        yielded command
    """
    yield f"data remove {get_target_type(target)} {target}"


def __wrap_source_type(source: SourceType) -> TargetType | Value:
    if isinstance(source, (Value, StoragePath, EntityPath, BlockPath)):
        return source
    source = as_nbt(source)
    return source
