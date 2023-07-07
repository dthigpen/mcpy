# Mcpy - A powerful Minecraft Datapack Builder

Build complex datapacks with ease using Python's expressive syntax and style!

- Avoid repetitive typing
- Bundle with dependencies
- Zip and release easily
- Take advantage of Python based Minecraft libraries like [Minecraft Data](https://github.com/PrismarineJS/minecraft-data)

```python
from mcpy import *

@datapack(include=['PlayerDB.v2.0.2.zip'])
def simple_datapack(ctx: Context):
    with namespace("simple_datapack"):
        with mcfunction("say_hello"):
            # yield commands in mcfunction context
            for i in range(3):
                yield f"say {i+1}.."
            yield "say Hello!"

            # Define helper functions
            yield from execute('if score #count dt.tmp matches 1..', [
                    'scoreboard players remove #count dt.tmp 1',
                    'function simple_datapack:say_hello'
                ])

        # Use functions from dependencies
        with mcfunction("save_data"):
            yield 'function #rx.playerdb:api/v2/get/self'
            yield 'data modify storage rx.playerdb:io player.data.cool_pack set value {eggs: 3b}'
            yield 'function #rx.playerdb:api/v2/save/self
```

## Get Started

Please see the [Get Started](tutorials/get-started.md) section for details!
