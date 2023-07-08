# Get Started

## Installation

First, make sure you have Python 3 installed. You can check by running the command `python --version`. If it returns an error you can download it from [here](https://www.python.org/downloads/) or using your package manager.

Create a directory for your datapack. For a simple datapack this can be directly in your world's datapacks folder. (e.g. `~/.minecraft/saves/<world>/datapacks/<your-datapack-name>`) Or anywhere else on the file system. Then navigate inside it
```
$ mkdir simple-datapack && cd simple-datapack
```

Create your project's Python environment and activate it. (This step is not strictly required but its a good practice!)

```
$ python -m venv env
$ source env/bin/activate
```

Install the `mcpy` package

```
$ pip install git+https://github.com/dthigpen/mcpy
```


Initialize the project. Hit enter to use default values

```
$ python -m mcpy init
```

## Building

Build your pack's `data/` files with the following. Optionally, add `-w` or `--watch` to continuously build on file changes

```
$ python -m mcpy build
```

Open the Minecraft World with the datapack we just created and reload datapacks using the `/reload` command.

That's it! You should see the hello message upon reload.

## Going further

Open up the `pack.py` file and inspect the lines. The concepts should look familiar (E.g. namespaces, `.mcfunction` files, and `JSON` files are written)

```python title="pack.py"
@datapack
def simple_pack():
    with namespace("simple_datapack"):
        with dir("api/greetings"):
            with mcfunction("hello"):
                yield "say Hello!"

    with namespace("minecraft"):
        with functions("load"):
            yield {"values": ["simple_datapack:api/greetings/hello"]}
```

Notice how namespaces and mcfunction files are entered. Anything indented under the `namespace` line will be applied under the `simple_datapack` namespace.

```python title="pack.py"
with namespace("simple_datapack"):
    ...
    with mcfunction("hello"):
    ...
```

Notice how lines are written to `.mcfunction` files. When Minecraft command strings are [yielded](https://docs.python.org/3/reference/expressions.html#yieldexpr) within the `mcfunction` context, they are written to the open `.mcfunction` file.

```python title="pack.py"
with mcfunction("hello"):
    yield 'say Hello There!'
```

Results in:

```mcfunction title="hello.mcfunction"
say Hello There!
```

Similarly, JSON based files like the `load.json` and `tick.json` files work in the same way except that we can yield a Python `dict` to represent the JSON structure.

```python title="pack.py"
with functions("load"):
    yield {"values": ["simple_datapack:api/greetings/hello"]}
```

Results in:

```json title="load.json"
{
    "values": [
        "simple_datapack:api/greetings/hello"
    ]
}
```

## Next Steps

- Check out the How-To Guides for more functionality
- Check out the [API Reference](../reference.md) for library details
