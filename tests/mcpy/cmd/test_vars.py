from mcpy.cmd.vars import *
from unittest.mock import patch
from mcpy.context import init_context
from mcpy.config import DEFAULT_CONFIG

def test_score_var():
    with init_context('fake_dir',DEFAULT_CONFIG):
        assert str(ScoreVar('foo')) == 'foo mcpy.var'
        assert str(ScoreVar()) == '$score0 mcpy.var'