from .nbt import Value, NbtPath, as_nbt, NbtPrimitive
from .util import tokens_to_str
from dataclasses import dataclass, field
from .nbt import Value, NbtPrimitive
from typing import Union, Iterator
from .scoreboard import Score, score_get
from .exec import execute
from ..context import write
from .tellraw import Tellable
from typing_extensions import Self


@dataclass
class DataCondition:
    """Parent class of data command container types that can be used in execute conditions"""

    def present(self) -> str:
        """condition for the existence of the this data path

        Returns:
            Condition string

        Example:
        ``` py
        @mcfunction
            def foo():
                data = EntityPath("SelectedItem", CurrentEntity())
                with execute(unless(data.present())):
                    ...
        ```
        """
        return f"data {get_target_type(self)} {self}"

    # TODO has_value condition
    def has_value(self, expected_value: any) -> str:
        """condition for the checking the value at a data path
        Args:
            expected_value: NBT value to compare against
        Returns:
            Condition string

        Example:
        ``` py
        @mcfunction
            def foo():
                data = EntityPath("SelectedItem", CurrentEntity())
                with execute(
                    unless(data.has_value({"id": "minecraft:apple", "Count": "1b"}))
                ):
                    ...
        ```
        """
        raise NotImplementedError()


@dataclass
class DataPath(NbtPath, DataCondition):
    """Base class to all data path types"""

    def to_score(self, holder: str = None, objective: str = None) -> Score:
        """Convert this data path to a score value

        Args:
            holder: score holder
            objective: score objective

        Returns:
            Score

        """
        score = Score(holder=holder, objective=objective)
        with execute(f"store result score {score}"):
            write(data_get(self))
        return score

    def set(self, value: any) -> Self:
        """Set the data path to the given value

        Args:
            value: Can be of any data path, NBT primitive, or Value type.

        Returns:
            Self

        """
        write(data_modify_set(self, value))
        return self

    def set_from_score(
        self, score: Score, result_type: str = "int", scale: int = 1
    ) -> Self:
        """Save the given score's value into this data path

        Args:
            score: source score
            result_type: data path data type
            scale: multiplier

        Returns:
            Self
        """
        write(
            f"execute store result storage {self} {result_type} {scale} run {score_get(score)}"
        )
        return self

    def merge(self, source: any, modify: bool=True) -> Self:
        """Merge the data source into this data path.

        Args:
            source: Source data type
            modify: Flag for using "data modify ... merge" or "data merge ..."

        Returns:
            Self
        """
        if modify:
            write(data_modify_merge(self, source))
        else:
            write(data_merge(self, source))
        return self

    def append(self, value: any) -> Self:
        """Append the value to the end of this data path

        Args:
            value: Source data type

        Returns:
            Self
        """
        write(data_modify_append(self, value))
        return self

    def remove(self) -> Self:
        """Remove the data at this data path

        Returns:
            Self
        """
        write(data_remove(self))
        return self


@dataclass
class StoragePath(DataPath, Tellable):
    """A container for a storage path"""

    namespace: str

    def to_tellable(self) -> dict:
        """Converts this container type to a tellraw printable element

        Returns:
            dict tellraw element
        """
        return {"nbt": self.path, get_target_type(self): self.namespace}

    def __str__(self):
        return tokens_to_str(self.namespace, self.path)


@dataclass
class EntityPath(DataPath, Tellable):
    """A container for an entity path"""

    selector: str

    def to_tellable(self) -> dict:
        """Converts this container type to a tellraw printable element

        Returns:
            dict tellraw element
        """
        return {"nbt": self.path, get_target_type(self): self.selector}

    def __str__(self):
        return tokens_to_str(self.selector, self.path)


@dataclass
class BlockPath(DataPath, Tellable):
    """A container for a block path"""

    pos: str

    def to_tellable(self) -> dict:
        """Converts this container type to a tellraw printable element

        Returns:
            dict tellraw element
        """
        return {"nbt": self.path, get_target_type(self): self.pos}

    def __str__(self):
        return tokens_to_str(self.pos, self.path)


TargetType = Union[StoragePath, EntityPath, BlockPath]
SourceType = Union[StoragePath, EntityPath, BlockPath, Value, NbtPrimitive]


def get_target_type(target: TargetType | Value) -> str:
    """Utility function for getting the string representation of the class type to be used in commands
    Args:
        target: data path, NBT primitive, or value type

    Returns:
        string representation of type
    
    Raises:
        ValueError: if given an unhandled container type
    
    Example:
    ``` python
    get_target_type(StoragePath('some.path','my_storage:'))
    # returns "storage"
    ```
    """
    if isinstance(target, EntityPath):
        return "entity"
    elif isinstance(target, StoragePath):
        return "storage"
    elif isinstance(target, BlockPath):
        return "block"
    elif isinstance(target, Value):
        return "value"
    raise ValueError(f"Unsupported target type: {type(target)}")


def data_get(target: TargetType) -> Iterator[str]:
    """Command template function for "data get ..."

    Args:
        target: target path

    Returns:
        yielded command
    """
    target_type = get_target_type(target)
    yield f"data get {target_type} {target}"


def data_modify_set(target: TargetType, source: SourceType) -> Iterator[str]:
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
    """Command template function for "data modify ... append ..."

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


def data_modify_merge(target: TargetType, source: SourceType) -> Iterator[str]:
    """Command template function for "data modify ... merge ..."

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
    yield f"data modify {target_type} {target} merge {source_type} {source}"


def data_merge(target: TargetType, source: Value) -> Iterator[str]:
    """Command template function for "data merge ..."

    Args:
        target: target path
        source: source path or value

    Returns:
        yielded command
    """
    raise NotImplementedError()


def data_remove(target: TargetType) -> Iterator[str]:
    """Command template function for "data remove ..."
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
