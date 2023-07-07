# mcpy

A library for writing Minecraft datapacks using the Python language.

```python
from mcpy import *

@datapack
def simple_pack(ctx: Context):
    with namespace("mypack"):
        with mcfunction("say_hello"):
            # in mcfunction context
            for i in range(3):
                yield f"say {i+1}.."
            yield "say Hello!"
```

```bash
> python -m mcpy
# Outputs the data dir:
# my-pack
# ├── data
# │   └── mypack
# │       └── say_hello.mcfunction
```

## Table of Contents

- [mcpy](#mcpy)
  - [Table of Contents](#table-of-contents)
  - [Motivation](#motivation)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Examples](#examples)
  - [Features](#features)
    - [Simple Syntax](#simple-syntax)
    - [Extensible](#extensible)
    - [Organize Complexity](#organize-complexity)

## Motivation

The `mcfunction` language is very limited and requires repetition and tedium for more complex tasks. There have been numerous attempts at extending it with custom languages and parsers but these have their own issues and create additional layers of complexity.

Advantages:

- Powerful - can utilize the full Python language and package ecosystem
- Extensible - With plain Python features (e.g. functions, vars, packages, etc) the language is easy to onto. (See Plugin examples)
- Minimal boilerplate - Not much overhead to write or think about when using Python syntax compared to other languages

Disadvantages:

- Syntax highlighting - Ability to use `mcfunction` syntax highlighting (such as with VSCode extensions) is lost since the commands are in `.py` files and `str`s. Though this could likely be worked around with a custom VSCode extension using embedded languages.

## Installation

1. Install the repository as a Python package

    ```bash
    > python -m pip install git+https://github.com/dthigpen/mcpy
    ```

## Usage

1. Prepare a directory for your new datapack. In your directory you will need a `pack.mcmeta` and a `src` folder for your Python code.

    For example with a datapack called `my_pack`:

    ```
    .
    └── my_pack
        ├── pack.mcmeta
        └── src
    ```

2. In `src/` create a `.py` file and use the `mcpy` library

    ```python
    from mcpy import *

    @datapack
    def simple_pack(ctx: Context):
        with namespace("mypack"):
            with mcfunction("say_hello"):
                # in mcfunction context
                for i in range(3):
                    yield f"say {i+1}.."
                yield "say Hello!"
    ```

3. Run the script from the `src` or datapack directory to generate the `data` folder with your pack contents.

    ```bash
    > python -m mcpy py_pack:run
    ```

## Examples

See the examples folder in this repository for full examples

## Features

### Simple Syntax

```python
# enter a namespace
with namespace('name'):
    ...
# (and implicit exit of each)

# enter a dir
with dir('name'):
    ...

# enter an mcfunction
with mcfunction('name'):
    ...

# enter a functions tag
with functions('name'):
    ...

# enter a blocks tag
with blocks('name'):
    ...
```

### Extensible

```python
# import using standard python
from mcpy_recurse import recurse
...
with recurse(some, args):
    yield 'say Over and over'
```

### Organize Complexity

```python
# organize with functions:
def lots_of_logic(greeting: str, start: int, end: int):
    for i in range(start, end):
        yield f'say {i}. {greeting}!'

# And call with
with mcfunction('my_thing'):
    yield from lots_of_logic('Hello', 1, 5)
```
