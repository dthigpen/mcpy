from dataclasses import dataclass
import functools
from .util import RootCmd, SubCmd, BaseCmd, EndCmd, tokens_to_str
from .common import Pos


class Data:
    class Target(RootCmd):
        def __init__(
            self,
            target_type: str,
            target: str,
            target_path: str = None,
        ) -> None:
            super().__init__(
                "data",
                template_args={
                    "target": target,
                    "target_type": target_type,
                    "target_path": target_path,
                },
            )

        def get(
            self,
            scale: int = None,
        ) -> str:
            return EndCmd(
                self,
                ["get $target_type $target", "$target_path", "$scale"],
                {"scale": scale},
            )

        def merge(self, nbt: str) -> str:
            return EndCmd(
                self,
                ["merge $target_type $target", "$nbt"],
                {"nbt": nbt},
            )

        def remove(
            self,
        ) -> str:
            return EndCmd(
                self,
                ["remove $target_type $target", "$target_path"],
            )

        def modify(self):
            return Data.ModifyCmd(self)

    class Entity(Target):
        def __init__(self, target: str, target_path: str = None) -> None:
            super().__init__("entity", target, target_path)

    class Block(Target):
        def __init__(self, target: Pos | str, target_path: str = None) -> None:
            super().__init__("block", str(target), target_path)

    class Storage(Target):
        def __init__(self, target: str, target_path: str = None) -> None:
            super().__init__("storage", target, target_path)

    class ModifyCmd(SubCmd):
        def __init__(
            self,
            parent: BaseCmd | str,
        ) -> None:
            super().__init__(
                parent,
                ["modify $target_type $target", "$target_path"],
            )

        def __action_from(
            self,
            action: str,
            source: any,  # "DataCmd.Block" | "DataCmd.Entity" | "DataCmd.Storage"
        ):
            return EndCmd(
                self,
                ["$action from $source_type $source", "$source_path"],
                source._template_args | {"action": action},
            )

        def __action_string(
            self,
            action: str,
            source: any,  # "DataCmd.Block" | "DataCmd.Entity" | "DataCmd.Storage" | str,
            start: int = None,
            end: int = None,
        ):
            return EndCmd(
                self,
                [
                    "$action from string $source_type $source",
                    "$source_path",
                    "$start $end",
                ],
                source._template_args
                | {
                    "action": action,
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
