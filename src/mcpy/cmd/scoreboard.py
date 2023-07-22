from .util import (
tokens_to_str
)

from .common import CmdObject
from dataclasses import dataclass

@dataclass
class Score(CmdObject):
    holder: str
    objective: str

    def __str__(self) -> str:
        return tokens_to_str(self.holder, self.objective)

