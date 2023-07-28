# from .selector import Selector
# from .nbt import *
from abc import ABC, abstractmethod

class Tellable(ABC):
    @abstractmethod
    def to_tellable(self) -> dict:
        pass
    
# def tellraw(entity_selector: Selector, *items: any):
    # res = []
    # for item in items:
    #     if isinstance(item, str):
    #         res.append(Str(item))
    #     elif isinstance(item, dict):
    #         res.append(NbtObj(item))
    # res = NbtList(res)
    # yield f'tellraw {entity_selector} {res}'