# Command API Reference

The command API is focused on making the built-in Minecraft commands easier to work with. The following are all included

## Container Types

Container types are for reusing data between commands. For example, 

```python
score = Score('holder','objective')
yield f'scoreboard players get {score}'
yield f'scoreboard players add {score}'
```

## Template Functions

Command template functions are used to build common commands up from variable arguments. For example:

```python
yield data.modify_set(some_data, {"value": 12, "foo": "bar"})
```

## Abstractions

Abstractions introduce higher-level programming concepts and abstract away Minecraft command-isms. For example,

```python
# create a function scope
with scope():
    # create safe scoped variables
    arr = Var().set([])
    item = Var()
    item.set({"value":5})
    arr.append(item)
```

## Data Command

::: mcpy.cmd.data

## Execute Command

::: mcpy.cmd.exec

## Scoreboard Command

::: mcpy.cmd.scoreboard

