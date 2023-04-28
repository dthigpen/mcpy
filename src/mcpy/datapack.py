from pathlib import Path
from .context import Context

class Datapack:
    def __init__(self, base_dir=None):
        if base_dir is None:
            cwd = Path.cwd()
            if cwd.joinpath("pack.mcmeta").is_file():
                base_dir = cwd
            elif cwd.parent.joinpath("pack.mcmeta").is_file():
                base_dir = cwd.parent
            else:
                raise ValueError(
                    "Must run from either the root of the datapack directory or inside the datapack-dir/src folder. Or manually pass in a directory with base_dir=<Path>"
                )
        base_dir = Path.cwd() if base_dir is None else Path(base_dir)
        self.ctx = Context(base_dir)
        self.builders = []

    def write(self, item: any) -> None:
        """Handle the given input depending on the current context"""
        if not self.ctx.input_handler:
            raise ValueError("Unknown context. Cannot handle input")
        self.ctx.input_handler(self.ctx, item)

    def build(self, *builder_fns):
        for builder in [*self.builders, *builder_fns]:
            items = builder(self.ctx)
            # TODO handle resetting ctx from one builder to another
            if items:
                for item in items:
                    self.write(item)

    def add_builder(self, func):
        self.builders.append(func)
        return func
