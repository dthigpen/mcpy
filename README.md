# mcpy

A library for writing Minecraft datapacks using the Python language. See the [mcpy Docs](https://dthigpen.github.io/mcpy/) for details.

```python
from mcpy import *

@datapack
def simple_pack():
    with namespace("mypack"):
        @mcfunction()
        def greet():
            yield "say Hello!"

        @mcfunction()
        def tick():
            # count down messages
            for i in range(3):
                yield f"say {i+1}.."
            # call greeting message
            greet()
```

```bash
> python -m mcpy build
# Outputs the data dir:
# my-pack
# ├── data
# │   └── mypack
# │       ├── greet.mcfunction
# │       └── tick.mcfunction
```

## Table of Contents

- [mcpy](#mcpy)
  - [Table of Contents](#table-of-contents)
  - [Motivation](#motivation)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Examples](#examples)

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

See the [Get Started](https://dthigpen.github.io/mcpy/tutorials/get-started/) Guide

## Examples

Full examples can be found in the `examples` directory of this repository.
