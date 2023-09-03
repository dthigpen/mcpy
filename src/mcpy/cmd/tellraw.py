'''
Module for all tellraw command container types and functions
'''
# from .selector import Selector
# from .nbt import *
from abc import ABC, abstractmethod

class Tellable(ABC):
    '''Interface implemented by container types to convert into a tellraw displayable type.
    '''
    @abstractmethod
    def to_tellable(self) -> dict:
        """Converts this container type to a tellraw printable element

        Returns:
            dict tellraw element
        """
        pass

def tellraw(entity_selector, *items: any) -> None:
    '''Not yet implemented'''
    raise NotImplementedError()
# def tellraw(entity_selector: Selector, *items: any):
    # res = []
    # for item in items:
    #     if isinstance(item, str):
    #         res.append(Str(item))
    #     elif isinstance(item, dict):
    #         res.append(NbtObj(item))
    # res = NbtList(res)
    # yield f'tellraw {entity_selector} {res}'