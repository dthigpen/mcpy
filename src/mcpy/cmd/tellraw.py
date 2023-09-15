'''
Module for all tellraw command container types and functions
'''
# from .selector import Selector
from .nbt import Str, NbtObj, NbtList
from abc import ABC, abstractmethod
from typing import Union
from ..context import write
class Tellable(ABC):
    '''Interface implemented by container types to convert into a tellraw displayable type.
    '''
    @abstractmethod
    def to_tellable(self) -> Union[dict,str]:
        """Converts this container type to a tellraw printable element

        Returns:
            dict or str tellraw element
        """
        pass

def tellraw(entity_selector, *items: Union[Tellable,str,dict]) -> None:
    '''Writes a tellraw command using the given items
    
    Args:
        entity_selector: Entity to tell the message to
        items: items to include in the tellraw command

    Example:
            ``` python
            foo_var = Var()
            foo_var.set(True)
            tellraw(CurrentEntity(),"Enabled: ", foo_var)
            ```
    '''
    res = []
    for item in items:
        if isinstance(item, Tellable):
            item = item.to_tellable()
        if isinstance(item, str):
            res.append(Str(item))
        elif isinstance(item, dict):
            res.append(NbtObj(item))
        else:
            raise ValueError(f'Unsupported tellraw argument: {item}. Use str(item) to use string representation.')
    res = NbtList(res)
    write(f'tellraw {entity_selector} {res}')