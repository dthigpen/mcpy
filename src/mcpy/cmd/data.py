from dataclasses import dataclass
import functools
from .util import (
    RootCmd,
    SubCmd,
    BaseCmd,
    EndCmd,
)


@dataclass
class Storage:
    target: str

    def __str__(self) -> str:
        return f"storage {self.target}"


@dataclass
class Entity:
    target: str

    def __str__(self) -> str:
        return f"entity {self.target}"


@dataclass
class Pos:
    x: str
    y: str
    z: str

    def __str__(self) -> str:
        return f"{self.x} {self.y} {self.z}"


@dataclass
class Block:
    pos: Pos | str

    def __str__(self) -> str:
        return f"block {self.pos}"


class DataCmd(RootCmd):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("data", *args, *kwargs)

    class ModifyCmd(SubCmd):
        def __init__(
            self,
            parent: BaseCmd | str,
            target: Block | Entity | Storage | str,
            target_path: str = None,
            *args,
            **kwargs,
        ) -> None:
            super().__init__(
                parent,
                ["modify $target", "$target_path"],
                template_args={"target": target, "target_path": target_path},
                *args,
                **kwargs,
            )

        def __action_from(
            self,
            action: str,
            source: Block | Entity | Storage | str,
            source_path: str = None,
        ):
            return EndCmd(
                self,
                ["$action from $source", "$source_path"],
                {"action": action, "source": source, "source_path": source_path},
            )

        def __action_string(
            self,
            action: str,
            source: Block | Entity | Storage | str,
            source_path: str = None,
            start: int = None,
            end: int = None,
        ):
            return EndCmd(
                self,
                ["$action from string $source", "$source_path", "$start $end"],
                {
                    "action": action,
                    "source": source,
                    "source_path": source_path,
                    "start": start,
                    "end": end,
                },
            )

        def __action_value(self, action: str, value: str):
            return EndCmd(
                self,
                ["$action value $value"],
                {
                    "action": action,
                    "value": value,
                },
            )

        append_from = functools.partialmethod(__action_from, "append")
        append_string = functools.partialmethod(__action_string, "append")
        append_value = functools.partialmethod(__action_value, "append")
        insert_from = functools.partialmethod(__action_from, "insert")
        insert_string = functools.partialmethod(__action_string, "insert")
        insert_value = functools.partialmethod(__action_value, "insert")
        merge_from = functools.partialmethod(__action_from, "merge")
        merge_string = functools.partialmethod(__action_string, "merge")
        merge_value = functools.partialmethod(__action_value, "merge")
        prepend_from = functools.partialmethod(__action_from, "prepend")
        prepend_string = functools.partialmethod(__action_string, "prepend")
        prepend_value = functools.partialmethod(__action_value, "prepend")
        set_from = functools.partialmethod(__action_from, "set")
        set_string = functools.partialmethod(__action_string, "set")
        set_value = functools.partialmethod(__action_value, "set")

    def get(
        self,
        target: Block | Entity | Storage | str,
        target_path: str = None,
        scale: int = None,
    ) -> str:
        return EndCmd(
            self,
            ["data get $target", "$target_path", "$scale"],
            {"target": target, "target_path": target_path, "scale": scale},
        )

    def merge(
        self, target: Block | Entity | Storage | str, nbt: str, target_path: str = None
    ) -> str:
        return EndCmd(
            self,
            ["data merge $target", "$target_path", "$nbt"],
            {"target": target, "target_path": target_path, "nbt": nbt},
        )

    def remove(
        self, target: Block | Entity | Storage | str, target_path: str = None
    ) -> str:
        return EndCmd(
            self,
            ["data remove $target", "$target_path"],
            {
                "target": target,
                "target_path": target_path,
            },
        )

    def modify(self, target: Block | Entity | Storage | str, target_path: str = None):
        return DataCmd.ModifyCmd(self, target, target_path=target_path)
