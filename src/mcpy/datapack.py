from .plugin import CorePlugin

class __Memoize:
    def __init__(self, f):
        self.f = f
        self.memo = {}

    def __call__(self, *args):
        return self.memo.setdefault(args, self.f(*args))


def Datapack(*args, plugins=None, **kwargs):
    if plugins is None:
        plugins = []

    @__Memoize
    def mix_in_plugins(*bases):
        class Datapack(*bases):
            pass

        return Datapack

    return mix_in_plugins(CorePlugin, *plugins)(*args, **kwargs)
