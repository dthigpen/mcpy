from mcpy import Datapack
from mcpy.cmd import *

def run():
    print('hello!')

    
if __name__ == "__main__":
    pack = Datapack()
    with pack.namespace("dt.example"):
        # define our on_load function
        with pack.mcfunction("on_load"):
            pack.write(
                """\
                scoreboard objectives add dt.example dummy
                scoreboard players reset * dt.example
                scoreboard players set $dt.ticker dt.example 0
                say Loaded Tick-And-Load
                """
            )
        # add it to the minecraft load tag
        with pack.namespace("minecraft"):
            with pack.functions("load"):
                pack.write({"values": ["dt.example:on_load"]})

        # now add our tick function
        with pack.mcfunction("on_tick"):
            def write_cmds():
                two_score = Player('$two', 'dt.example')
                five_score = Player('$five', 'dt.example')
                mod_five_score = Player('$dt.mod5', 'dt.example')
                tmp_score = Player('$dt.tmp', 'dt.example')
                ticker_score = Player('$dt.ticker', 'dt.example')
            
                yield two_score.set(2)
                yield five_score.set(5)
                yield mod_five_score.reset()
                yield tmp_score.assign(ticker_score)
                yield tmp_score.mod(five_score)
                yield f"""\
                execute if score $dt.tmp dt.example matches 0 run scoreboard players set $dt.mod5 dt.example 1
                execute if score $dt.mod5 dt.example matches 1 run scoreboard players operation $dt.tmp dt.example = $dt.ticker dt.example
                execute if score $dt.mod5 dt.example matches 1 run scoreboard players operation $dt.tmp dt.example %= $two dt.example
                execute if score $dt.mod5 dt.example matches 1 if score $dt.tmp dt.example matches 0 run say Tick!
                execute if score $dt.mod5 dt.example matches 1 unless score $dt.tmp dt.example matches 0 run say Tock!
                scoreboard players add $dt.ticker dt.example 1
                """
            pack.write(write_cmds())

        # and add it to the minecraft tick tag
        with pack.namespace("minecraft"):
            with pack.functions("tick"):
                pack.write({"values": ["dt.example:on_tick"]})
        print("DONE")
