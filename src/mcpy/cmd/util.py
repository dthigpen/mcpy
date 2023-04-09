from abc import ABC, abstractmethod
from string import Template
import re

def tokens_to_str(*tokens):
    tokens = filter(bool, tokens)
    tokens = map(lambda t: str(t), tokens)
    tokens = filter(bool, tokens)

    return " ".join(tokens) if tokens else ""


def run_templates_to_str(template_str_or_list: str | list[str], template_args: dict):
    template_str_list = (
        template_str_or_list
        if isinstance(template_str_or_list, list)
        else [template_str_or_list]
    )
    template_args = {k: ('' if v is None else v) for k,v in template_args.items()}
    cmd_tokens = [Template(t).substitute(template_args) for t in template_str_list]
    return tokens_to_str(*cmd_tokens)


class BaseCmd(ABC):
    def __init__(
        self,
        parent: 'BaseCmd',
        template_str_or_list: str | list[str],
        template_args=None,
    ) -> None:
        self.__parent = parent
        self.__template_str_list = (
            template_str_or_list
            if isinstance(template_str_or_list, list)
            else [template_str_or_list]
        )
        self.__template_args = template_args if template_args else {}

    def __str__(self) -> str:
        raise ValueError("Unable to convert to string")

    def __convert(self, *suffix_tokens: str) -> str:
        prefix = self.__parent.__convert() if self.__parent else ""
        cmd = run_templates_to_str(self.__template_str_list, self.__template_args)
        return tokens_to_str(prefix, cmd, *suffix_tokens)


class RootCmd(BaseCmd):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(None, *args, **kwargs)


class SubCmd(BaseCmd, ABC):
    def __init__(self, parent: BaseCmd | str, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

class EndCmd(BaseCmd):
    def __str__(self) -> str:
        return self.__convert()