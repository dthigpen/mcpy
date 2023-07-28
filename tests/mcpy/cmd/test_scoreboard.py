from mcpy.cmd.scoreboard import *
# from .util import assert_as_str

def assert_as_str(actual: any, expected: str):
    assert str(actual) == expected

def assert_gen_lines(actual: any, expected: str):
    lines = '\n'.join(actual)
    assert lines == expected

def test_score():
    assert_as_str(Score('player','obj'),'player obj')

def test_scoreboard():
    score = Score('foo','obj')
    assert_gen_lines(score_enable(score), 'scoreboard players enable foo obj')
    assert_gen_lines(score_reset(score), 'scoreboard players reset foo obj')
    assert_gen_lines(score_get(score), 'scoreboard players get foo obj')
