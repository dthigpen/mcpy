from .scoreboard import MCPY_SCORE_OBJECTIVE
from ..context import write
def init_cmds():
    cmds = (
        f'scoreboard objectives add {MCPY_SCORE_OBJECTIVE} dummy',
        f'scoreboard objectives add dt.tmp dummy',
    )
    for cmd in cmds:
        write(cmd)