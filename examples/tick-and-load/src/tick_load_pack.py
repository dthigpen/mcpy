from mcpy import Datapack

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
            pack.write(
                """\
            scoreboard players set $two dt.example 2
            scoreboard players set $five dt.example 5
            scoreboard players reset $dt.mod5 dt.example
            scoreboard players operation $dt.tmp dt.example = $dt.ticker dt.example
            scoreboard players operation $dt.tmp dt.example %= $five dt.example
            execute if score $dt.tmp dt.example matches 0 run scoreboard players set $dt.mod5 dt.example 1
            execute if score $dt.mod5 dt.example matches 1 run scoreboard players operation $dt.tmp dt.example = $dt.ticker dt.example
            execute if score $dt.mod5 dt.example matches 1 run scoreboard players operation $dt.tmp dt.example %= $two dt.example
            execute if score $dt.mod5 dt.example matches 1 if score $dt.tmp dt.example matches 0 run say Tick!
            execute if score $dt.mod5 dt.example matches 1 unless score $dt.tmp dt.example matches 0 run say Tock!
            scoreboard players add $dt.ticker dt.example 1
            """
            )

        # and add it to the minecraft tick tag
        with pack.namespace("minecraft"):
            with pack.functions("tick"):
                pack.write({"values": ["dt.example:on_tick"]})
