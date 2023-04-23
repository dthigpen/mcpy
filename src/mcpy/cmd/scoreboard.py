from .util import (
    RootCmd,
    SubCmd,
    BaseCmd,
    EndCmd,
)


class Scoreboard(RootCmd):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("scoreboard", *args, **kwargs)

    class Objective(SubCmd):
        def __init__(self, parent: BaseCmd | str, *args, **kwargs) -> None:
            super().__init__(parent, "objectives", *args, **kwargs)

        def list(self):
            return EndCmd(self, "list")

        def add(self, objective: str, criteria: str, display_name: str = None):
            return EndCmd(
                self,
                ["add $objective $criteria", "$display_name"],
                {
                    "objective": objective,
                    "criteria": criteria,
                    "display_name": display_name,
                },
            )

    def objectives(self, *args, **kwargs):
        return Scoreboard.Objective(self, *args, **kwargs)

    class Player(SubCmd):
        def __init__(self, name: str, objective: str, *args, **kwargs) -> None:
            super().__init__(
                Scoreboard(),
                "players",
                template_args={"name": name, "objective": objective},
                *args,
                **kwargs,
            )

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


# Re define at top-level
class Player(Scoreboard.Player):
    pass

