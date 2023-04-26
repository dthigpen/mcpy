from .util import (
    RootCmd,
    SubCmd,
    BaseCmd,
    EndCmd,
)

from typing import Union


class Scoreboard:
    class Objectives(RootCmd):
        def __init__(self) -> None:
            super().__init__('scoreboard objectives')

        def list(self):
            return EndCmd(self, "list")

        def add(self, objective: str, criteria="dummy", display_name=None):
            return Scoreboard.Objective(objective, criteria=criteria, display_name=display_name).add()

    class Objective(SubCmd):
        def __init__(self, objective: str, criteria="dummy", display_name=None) -> None:
            super().__init__(
                Scoreboard.Objectives(),
                '',
                template_args={
                    "objective": objective,
                    "criteria": criteria,
                    "display_name": display_name,
                },
            )

        def add(self):
            return EndCmd(
                self,
                ["add $objective $criteria", "$display_name"],
            )

    def objectives():
        return Scoreboard.Objectives()

    class Player(RootCmd):
        def __init__(
            self, name: str, objective: Union["Scoreboard.Objective", str]
        ) -> None:
            template_args = {"name": name}
            if isinstance(objective, Scoreboard.Objective):
                template_args = template_args | objective._template_args
            else:
                template_args = template_args | {"objective": objective}
            super().__init__("scoreboard players", template_args=template_args)

        def set(self, score: int):
            return EndCmd(
                self, "set $name $objective $score", template_args={"score": score}
            )

        def reset(self):
            return EndCmd(self, "reset $name $objective")

        class Operation(SubCmd):
            def __init__(self, parent: BaseCmd | str, *args, **kwargs) -> None:
                super().__init__(
                    parent,
                    "operation $name $objective",
                    *args,
                    **kwargs,
                )

            def __operation(self, operation: str, source_player: "Scoreboard.Player"):
                return EndCmd(
                    self,
                    "$operation $name $objective",
                    source_player._template_args | {"operation": operation},
                )

            def assign(self, source_player: "Scoreboard.Player"):
                return self.__operation("=", source_player)

            def add(self, source_player: "Scoreboard.Player"):
                return self.__operation("+=", source_player)

            def subtract(self, source_player: "Scoreboard.Player"):
                return self.__operation("-=", source_player)

            def multiply(self, source_player: "Scoreboard.Player"):
                return self.__operation("*=", source_player)

            def divide(self, source_player: "Scoreboard.Player"):
                return self.__operation("/=", source_player)

            def mod(self, source_player: "Scoreboard.Player"):
                return self.__operation("%=", source_player)

            def swap(self, source_player: "Scoreboard.Player"):
                return self.__operation("><", source_player)

            def min(self, source_player: "Scoreboard.Player"):
                return self.__operation("<", source_player)

            def max(self, source_player: "Scoreboard.Player"):
                return self.__operation(">", source_player)

        def operation(self):
            return Scoreboard.Player.Operation(self)

    def players(self, name: str, objective: str):
        return Scoreboard.Player(name, objective)
