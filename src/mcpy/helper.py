from .context import Context
from mcpy_cmd import StoragePath, Value, Score, BlockPath
from mcpy_cmd.data import modify_set
class Var:
    def __init__(self, ctx: Context, name: str, prefix='this.',namespace='call_stack:') -> None:
        self.storage_path = StoragePath(namespace, f'{prefix}{name}')
        self.ctx = ctx

    def assign(self, source: Value | StoragePath | BlockPath | Score | str) -> None:
        self.ctx.write(modify_set(self.storage_path, source))

class VarHelper:

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx
        self.state_map = {}
        self.var_count = 0

    def new(self, source: Value | StoragePath | BlockPath | Score | str, name=None) -> Var:
        if name is None:
            name = f'var{self.var_count}'
            self.var_count += 1
        
        var = self.get(name)
        var.assign(source)
        return var
    
    def get(self, name: str) -> Var:
        return Var(self.ctx, name)
    