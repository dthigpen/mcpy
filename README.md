# mcpy

A library for writing Minecraft datapacks in Python syntax

## Examples

```python
pack = Datapack()
def build():
    with pack.namespace("mypack"):
        # namespace context

        with pack.dir("api"):
            # in dir context

            with pack.mcfunction("say_hello"):
                # in mcfunction context
                for i in range(3, 0, -1):
                    yield f"say {i}.."
                yield "say Hello!"
pack.build(build())
```
Which outputs:
```
.
├── data
│   └── mypack
│       └── functions
│           └── api
│               └── say_hello.mcfunction
```
