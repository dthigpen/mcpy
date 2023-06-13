# How to include datapack dependencies

First, ensure that you have the dependency datapacks (either zip or directory) near your project to make it easy to find. For example:

```
/libs/
    some_dep.zip
    cool_lib/
my_datapack/
```

Next, reference the ones you want in you `pack.py` file's `@datapack` decorator. Inside the datapack function you can call their functions and data as normal.

```python title="pack.py"
@datapack(include=['libs/some_dep.zip','libs/cool_lib'])
def my_datapack(ctx: Context):
    ...
```

Finally, in order to bundle the dependencies with the datapack the `-o` or `--output-dir` must be specified. This will a directory where `mcpy` should copy the final datapack into. This could be anywhere, but we will use a world's datapack folder so we can instantly use it.

```
python -m mcpy build -o ~/.minecraft/saves/my_world/datapacks
```

Now open the Minecraft world and enter the `/reload` command.
