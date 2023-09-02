# Working With Commands

There are several ways to write mcfunction commands in Mcpy, each have their different advantages and disadvantages.

## Command Strings

Command strings represent the exact command that will be written, making them a great fallback when the other options are not available.

``` python
@mcfunction
def my_function():
    yield 'scoreboard players set $two dt.example 2'
    yield 'scoreboard players operation $count dt.example += $two dt.example'
```

Python's `f-string`s can be used to make them slightly less verbose.

``` python
@mcfunction
def my_function():
    two = '$two'
    obj = 'dt.example'

    yield f'scoreboard players set {two} {obj} 2'
    yield f'scoreboard players operation $count {obj} += $two {obj}'
```

Lastly, command strings can be yielded as shown above or written with the `write` function.

``` python
@mcfunction
def my_function():
    two = '$two'
    obj = 'dt.example'

    write(f'scoreboard players set {two} {obj} 2')
    write( f'scoreboard players operation $count {obj} += $two {obj}')
```

## Container Types

Container types are for reusing data between commands.

```python
@mcfunction
def my_function():
    count = Score('$count','dt.example')
    two = Score('$two','dt.example')
    yield f'scoreboard players set {two} 2'
    yield f'scoreboard players operation {count} += {two}'
```

The `Score` container's string representation is the `<holder> <objective>` since these are often found together in commands.

Most container types also have functions that take in arguments and automatically write commands with them, greatly reducing the verbosity and boilerplate code.

```python
@mcfunction
def my_function():
    count = Score('$count','dt.example')
    two = Score('$two','dt.example').set(2)
    count.add(two)
```

Additionally, most container types can generate their constructor inputs. For example, `Score()` can be used on its own without supplying a holder and objective string.

```python
@mcfunction
def my_function():
    count = Score()
    two = Score().set(2)
    count.add(two)
```

## Command Template Functions

In between command strings and container types are command template functions. These are functions that build common commands up from variable arguments.

```python
@mcfunction
def my_function():
    yield data.modify_set(some_data, {"value": 12, "foo": "bar"})
```

Typically command template functions yield back one or more commands.

## Abstractions

Abstractions introduce higher-level programming concepts and abstract away Minecraft command-isms.

```python
# create a function scope
with scope():
    # create safe scoped variables
    arr = Var().set([])
    item = Var()
    item.set({"value":5})
    arr.append(item)
```

In this example, we initialized a variable, set its value to an empty array, and appended another variable to it that had a value of `{value: 5}`.

See the [Command Reference](cmd_reference.md) for more container types.
