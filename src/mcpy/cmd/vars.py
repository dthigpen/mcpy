from __future__ import annotations
import contextlib
from dataclasses import dataclass, field

from ..context import write, get_global_context, get_context
from ..decorators import mcfunction, FunctionResource
from .scoreboard import Score, score_get
from .data import *
from .tag import Tag
from .nbt import Value, NbtPrimitive
from .function import function
from typing import Union, Callable
from .util import tokens_to_str
from .exec import execute
from .tellraw import Tellable
TargetType = Union[StoragePath, EntityPath, BlockPath]
SourceType = Union[StoragePath, EntityPath, BlockPath, Value, NbtPrimitive]


@contextlib.contextmanager
def scope():
    write('function call_stack:push')
    # write(f'say called {get_context().get_path().stem}')
    yield
    write('function call_stack:pop')

CALL_STACK_NAMESPACE = 'call_stack:'

@dataclass
class Var(StoragePath, Tellable):
    path: str = None
    prefix: str = 'this'
    namespace: str = field(default=CALL_STACK_NAMESPACE, init=False)
    
    '''Storage based container for scoped variable data'''
    def __post_init__(self):
        
        if self.path is None:
            count = get_global_context().increment_count('var_count')
            self.path = f'var{count}'
    
    def __str__(self) -> str:
        return tokens_to_str(self.namespace, f'{self.prefix}.{self.path}')
        

    def copy(self, name=None) -> Var:
        '''Copy this variable to a new variable'''
        new_var = Var(path=name)
        new_var.set(self)
        return new_var
    

    def to_tellable(self) -> dict:
        return {"nbt": f'{self.prefix}.{self.path}', get_target_type(self): self.namespace}
    

@dataclass
class CallVar(Var):
    prefix: str = field(default='call',init=False)

arg0 = Var('arg0')
arg1 = Var('arg1')
arg2 = Var('arg2')
arg3 = Var('arg3')
arg4 = Var('arg4')
arg5 = Var('arg5')
arg6 = Var('arg6')
arg7 = Var('arg7')
arg8 = Var('arg8')
arg9 = Var('arg9')
ret_var = Var('return')
call_ret_var = CallVar('return')
call_arg0 = CallVar('arg0')
call_arg1 = CallVar('arg1')
call_arg2 = CallVar('arg2')
call_arg3 = CallVar('arg3')
call_arg4 = CallVar('arg4')
call_arg5 = CallVar('arg5')
call_arg6 = CallVar('arg6')
call_arg7 = CallVar('arg7')
call_arg8 = CallVar('arg8')
call_arg9 = CallVar('arg9')

def call(resource_str: str, *call_args, extra_args=None) -> Var:
    for i, arg in enumerate(call_args):
        CallVar(f'arg{i}').set(arg)
    if extra_args is not None:
        for name, value in extra_args:
            CallVar(name).set(value)
    write(function(resource_str))
    return CallVar('return')


class ScopedFunctionResource(FunctionResource):
    def __call__(self, *args, extra_args = None) -> Var:
        return call(self.path, *args, extra_args=extra_args)
    
def scoped_mcfunction(generator_fn: Callable[[],Iterator]=None, *, name:str = None, **kwargs: any) -> ScopedFunctionResource:
    """A decorator for creating a scoped mcfunction file to use variables.
    
    The generator function can yield command strings or call write(<cmd>)

    Args:
        generator_fn: Generator function to build the file from
        name: The name of the file, overrides the decorated function's name
        kwargs: extra arguments to be passed to the underlying file function

    Example:
        ``` py
        @scoped_mcfunction
        def greet():
            foo = Var()
            var.set(2)
            bar = some_scoped_function(foo).copy()
            ret_var.set(bar)
        ```
    """

    def decorator_mcfunction(func):

        def wrapped_callable():
            with scope():
                return func()
        wrapped_callable.__name__ = func.__name__
        return ScopedFunctionResource(mcfunction(wrapped_callable, name=name, **kwargs).path)

    if generator_fn is None:
        print('non')
        return decorator_mcfunction
    else:
        print('scoped_mcfunction decorator_mcfunction with func')
        return decorator_mcfunction(generator_fn)