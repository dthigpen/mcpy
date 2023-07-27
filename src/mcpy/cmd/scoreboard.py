from .util import (
tokens_to_str
)

from .common import CmdObject
from dataclasses import dataclass

@dataclass
class Score(CmdObject):
    '''Container to hold a score holder and objective'''
    holder: str
    objective: str

    def __str__(self) -> str:
        return tokens_to_str(self.holder, self.objective)


def get(score: Score):
    '''Command to get a player score'''
    yield f'scoreboard players get {score}'