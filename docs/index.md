# Mcpy - A powerful Minecraft Datapack Builder

Build complex datapacks with ease using Python's expressive syntax and style!

## Examples

Avoid repetitive typing:

```python
from mcpy import *

@datapack
def simple_datapack(ctx: Context):
    with namespace(ctx, "simple_datapack"):
        with mcfunction(ctx, "say_hello"):
            # yield lines in mcfunction context
            for i in range(3):
                yield f"say {i+1}.."
            yield "say Hello!"
```

Even include datapacks as dependencies:

```python
@datapack(include=['PlayerDB.v2.0.2.zip'])
def my_pack(ctx: Context):
    with namespace(ctx, "simple_datapack"):
        with mcfunction(ctx, "do_thing"):
            yield 'data modify storage rx.playerdb:io player.data.cool_pack set value {eggs: 3b}'
    ...
```

## Get Started

Please see the [Get Started](tutorials/get-started.md) section for details!
