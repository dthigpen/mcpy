# mcpy

A library for writing Minecraft datapacks in Python syntax

## Example

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
    # py_pack.py
    from mcpy import Datapack

        if __name__ == '__main__':
            pack = Datapack()
            def builder():
                with pack.namespace('mypack'):
                    with pack.mcfunction('my_func'):
                        yield 'Hello from my func'
            pack.build(builder())
    ```

3. Run the script from the `src` or datapack directory to generate the `data` folder with your pack contents.

    ```bash
    > python my_pack.py
    ```

## TODO

1. Add json_file support
1. Add formatter
1. Add file marker check so that non mcpy files are not overwritten
1. Add tests
1. Explore plugin system
