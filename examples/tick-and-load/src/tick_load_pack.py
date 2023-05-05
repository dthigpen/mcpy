from mcpy import *
from mcpy_cmd import *

def run(ctx: Context):
    pack_namespace = "dt.example"
    pack_objective = Scoreboard.Objective(pack_namespace)
    with namespace(ctx, "dt.example"):
        # define our on_load function
        with mcfunction(ctx, "on_load"):
            yield pack_objective.add()
            yield Scoreboard.Player("*", pack_objective).reset()
            ticker_score = Scoreboard.Player("$dt.ticker", "dt.example")
            yield ticker_score.set(0)
            yield "say Loaded Tick-And-Load"
        # add it to the minecraft load tag
        with namespace(ctx, "minecraft"):
            with functions(ctx, "load"):
                yield {"values": ["dt.example:on_load"]}

        # now add our tick function
        with mcfunction(ctx, "on_tick"):
            two_score = Scoreboard.Player("$two", "dt.example")
            five_score = Scoreboard.Player("$five", "dt.example")
            mod_five_score = Scoreboard.Player("$dt.mod5", "dt.example")
            tmp_score = Scoreboard.Player("$dt.tmp", "dt.example")
            ticker_score = Scoreboard.Player("$dt.ticker", "dt.example")

            yield two_score.set(2)
            yield five_score.set(5)
            yield mod_five_score.reset()
            yield tmp_score.operation().assign(ticker_score)
            yield tmp_score.operation().mod(five_score)
            yield f"""\
            execute if score $dt.tmp dt.example matches 0 run scoreboard players set $dt.mod5 dt.example 1
            execute if score $dt.mod5 dt.example matches 1 run scoreboard players operation $dt.tmp dt.example = $dt.ticker dt.example
            execute if score $dt.mod5 dt.example matches 1 run scoreboard players operation $dt.tmp dt.example %= $two dt.example
            execute if score $dt.mod5 dt.example matches 1 if score $dt.tmp dt.example matches 0 run say Tick!
            execute if score $dt.mod5 dt.example matches 1 unless score $dt.tmp dt.example matches 0 run say Tock!
            scoreboard players add $dt.ticker dt.example 1
            """

        # and add it to the minecraft tick tag
        with namespace(ctx, "minecraft"):
            with functions(ctx, "tick"):
                yield {"values": ["dt.example:on_tick"]}



if __name__ == "__main__":
    run()
