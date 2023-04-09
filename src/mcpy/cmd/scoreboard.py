from dataclasses import dataclass
from .util import (
    RootCmd,
    SubCmd,
    BaseCmd,
    EndCmd,
)

@dataclass
class Player:
    name: str
    objective: str

    def __str__(self) -> str:
        return f"{self.name} {self.objective}"


class ScoreboardCmd(RootCmd):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("scoreboard", *args, **kwargs)

    class ObjectivesCmd(SubCmd):
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

    def objectives(self):
        return ScoreboardCmd.ObjectivesCmd()

    class PlayersCmd(SubCmd):
        def __init__(self, parent: BaseCmd | str, *args, **kwargs) -> None:
            super().__init__(parent, "players", *args, **kwargs)

        def set(self, player: Player, score: int):
            return EndCmd(
                self,
                "set $player $score",
                {
                    "player": player,
                    "score": score,
                },
            )

        def reset(self, player: Player):
            return EndCmd(
                self,
                "reset $player",
                {
                    "player": player,
                },
            )

        class OperationCmd(SubCmd):
            def __init__(
                self, parent: BaseCmd | str, target_player: Player, *args, **kwargs
            ) -> None:
                super().__init__(
                    parent,
                    "operation $target_player",
                    template_args={"target_player": target_player},
                    *args,
                    **kwargs,
                )

            def __operation(self, operation: str, source_player: Player):
                return EndCmd(
                    self,
                    "$operation $source_player",
                    {
                        "operation": operation,
                        "source_player": source_player,
                    },
                )

            def assign(self, source_player: Player):
                return self.__operation("=", source_player)

            def add(self, source_player: Player):
                return self.__operation("+=", source_player)

            def subtract(self, source_player: Player):
                return self.__operation("-=", source_player)

            def multiply(self, source_player: Player):
                return self.__operation("+=", source_player)

            def divide(self, source_player: Player):
                return self.__operation("/=", source_player)

            def mod(self, source_player: Player):
                return self.__operation("%=", source_player)

            def swap(self, source_player: Player):
                return self.__operation("><", source_player)

            def min(self, source_player: Player):
                return self.__operation("<", source_player)

            def max(self, source_player: Player):
                return self.__operation(">", source_player)

        def operation(self, target_player: Player):
            return ScoreboardCmd.PlayersCmd.OperationCmd(self, target_player)

    def players(self):
        return ScoreboardCmd.PlayersCmd(self)

