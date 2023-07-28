# Get Started

## Installation

First, make sure you have Python 3 installed. You can check by running the command `python --version`. If it returns an error you can download it from [here](https://www.python.org/downloads/) or using your package manager.

Create a directory for your datapack. For a simple datapack this can be directly in your world's datapacks folder. (e.g. `~/.minecraft/saves/<world>/datapacks/<your-datapack-name>`) Or anywhere else on the file system. Then navigate inside it

``` bash
mkdir simple-datapack && cd simple-datapack
```

Create your project's Python environment and activate it. (This step is not strictly required but its a good practice!)

```bash
python -m venv env
source env/bin/activate
```

Install the `mcpy` package

```bash
pip install git+https://github.com/dthigpen/mcpy
```

Initialize the project. Hit enter to use default values

```bash
python -m mcpy init
```

Open up the `src/pack.py` file and inspect the lines. The concepts should look familiar (E.g. namespaces, `.mcfunction` files, and `JSON` files are written)

```python title="pack.py"
@datapack
def simple_pack():
    with namespace("simple_datapack"):
        with directory("api/greetings"):
            @mcfunction
            def say_hello():
                yield "say Hello!"

    with namespace("minecraft"):
        @functions
        def load():
            yield {"values": ["simple_datapack:api/greetings/say_hello"]}
```

## Building

Build your pack's `data/` files with the following. Optionally, add `-w` or `--watch` to continuously build on file changes

```
python -m mcpy build
```

Open the Minecraft World with the datapack we just created and reload datapacks using the `/reload` command.

That's it! You should see the hello message upon reload.

## Writing a Datapack

First, create a `src/pack.py` file in your datapack directory or use `python -m mcpy init` to get a starter file.

In this file, Mcpy will look for a function with a `@datapack` decorator. This function will define your datapack and all of its files.

``` python title="pack.py"
from mcpy import (datapack, mcfunction, functions)

@datapack
def my_pack():
    # define datapack here
    ...
```

Before defining any files, a namespace must be defined (e.g. `pack/data/<namespace>/functions/foo.mcfunction`). Use the `namespace` context manager to descend into a namespace directory.

``` python title="pack.py"

@datapack
def my_pack():
    with namespace('my.pack'):
        # files and directories defined here
        ...
```

Now that a namespace is created, an mcfunction file can be created by defining a function decorated with `@mcfunction`.

``` python title="pack.py"

@datapack
def my_pack():
    with namespace('my.pack'):
        @mcfunction
        def say_hello():
            yield 'say Hello!'
```

In the example above, the `.mcfunction` file generated will have the name `say_hello`, taken from the decorated function. Similarly, the content will be taken from the yielded command strings or written using the `write` function.

``` python
...
    @mcfunction
    def say_hello():
        yield 'say Hello!'
        write('say There!')
```

(Additionally, the `mcpy.cmd` module can be used to simplify usage of common commands)

Now that the mcfunction is defined. We can call it when the datapack loads using the `minecraft:load` tag. Function tag files are defined in a similar manner as above.

``` python title="pack.py"

@datapack
def my_pack():
    with namespace('my.pack'):
        @mcfunction
        def say_hello():
            yield 'say Hello!'
    
    with namespace('minecraft'):
        @functions
        def load():
            yield {
                'values': [ str(say_hello) ]
            }
```

Now the datapack can be built from it's root directory (e.i. with the `pack.mcmeta` in it).

``` bash
python -m mcpy build --watch
```

The `data` directory will now be populated with the expected files and the datapack directory can be copied into a world. Alternatively, an output directory can be specified that the compiled datapack will be copied into. Using an output directory is required when including dependency datapacks. (See the [How to Include Dependencies](https://dthigpen.github.io/mcpy/user-guides/how-to-include-dependencies/) guide for details) 

``` bash
python -m mcpy build --watch -o ~/.minecraft/saves/my_world/datapacks
```

The last step is to open the Minecraft world and run the `/reload` command to see the changes take effect.

## Next Steps

- [Working With Commands](working-with-commands.md)
- [API Reference](reference.md)
