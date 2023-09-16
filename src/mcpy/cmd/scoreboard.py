from __future__ import annotations
from .util import (
tokens_to_str
)

from ..context import write, get_global_context
from .block import CmdObject
from .tellraw import Tellable
from dataclasses import dataclass

MCPY_SCORE_OBJECTIVE = 'mcpy.var'

@dataclass
class ScoreCondition:
    
    def equals(self, other: Score) -> str:
        return f'score {self} = {other}'
    
    def matches(self, score_range: str) -> str:
        return f'score {self} matches {score_range}'
    
@dataclass
class Score(CmdObject, ScoreCondition, Tellable):
    '''Container to hold a score holder and objective'''
    holder: str = None
    objective: str = None

    def __post_init__(self):
        if self.holder is None:
            count = get_global_context().increment_count('var_count')
            self.holder = f'$score{count}'
        if self.objective is None:
            self.objective = MCPY_SCORE_OBJECTIVE

    def __str__(self) -> str:
        return tokens_to_str(self.holder, self.objective)

    def get(self) -> Score:
        '''Command to get a player score'''
        write(score_get(self))
        return self
    
    def set(self) -> Score:
        '''Command to set a player score'''
        write(score_set(self))
        return self

    def remove(self, count:int = 1) -> Score:
        '''Command to remove an amount from a player score'''
        write(score_remove(self, count))
        return self
    
    def add(self, count:int = 1) -> Score:
        '''Command to add an amount to a player score'''
        write(score_add(self, count))
        return self
    
    def reset(self) -> Score:
        '''Command to reset a player score'''
        write(score_reset(self))
        return self

    def enable(self) -> Score:
        '''Command to enable a player score'''
        write(score_enable(self))
        return self
    
    def to_tellable(self) -> dict:
        return {"score":{"name":self.holder,"objective":self.objective}}
        

def score_get(score: Score):
    '''Command to get a player score'''
    yield f'scoreboard players get {score}'

def score_set(score: Score):
    '''Command to set a player score'''
    yield f'scoreboard players set {score}'


def score_remove(score: Score, count: int = 1):
    '''Command to remove an amount from a player score'''
    yield f'scoreboard players remove {score} {count}'

def score_add(score: Score, count: int = 1):
    '''Command to add an amount to a player score'''
    yield f'scoreboard players add {score} {count}'

def score_reset(score: Score):
    '''Command to reset the score'''
    yield f'scoreboard players reset {score}'

def score_enable(score: Score):
    '''Command to enable the score'''
    yield f'scoreboard players enable {score}'

def score_objectives_add(name: str, type: str = None):
    '''Command to add an objective. Type defaults to "dummy"'''
    if type is None:
        type = 'dummy'
    yield f'scoreboard objectives add {name} {type}'