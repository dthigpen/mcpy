from .plugin import CorePlugin
from pathlib import Path

class __Memoize:
    def __init__(self, f):
        self.f = f
        self.memo = {}

    def __call__(self, *args):
        return self.memo.setdefault(args, self.f(*args))


def Datapack(*args, base_dir=None, plugins=None, **kwargs):
    if base_dir is None:
        cwd = Path.cwd()
        if cwd.joinpath('pack.mcmeta').is_file():
            base_dir = cwd
        elif cwd.parent.joinpath('pack.mcmeta').is_file():
            base_dir = cwd.parent
        else:
            raise ValueError('Must run from either the root of the datapack directory or inside the datapack-dir/src folder. Or manually pass in a directory with base_dir=<Path>')
    if plugins is None:
        plugins = []

    @__Memoize
    def mix_in_plugins(*bases):
        class Datapack(*bases):
            pass

        return Datapack

    return mix_in_plugins(CorePlugin, *plugins)(base_dir=base_dir, *args, **kwargs)
