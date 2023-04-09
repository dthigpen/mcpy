# Built with mcpy (https://github.com/dthigpen/mcpy)

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
