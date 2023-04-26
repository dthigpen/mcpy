from abc import ABC, abstractmethod
from string import Template
import re


def tokens_to_str(*tokens):
    tokens = filter(bool, tokens)
    tokens = map(lambda t: str(t), tokens)
    tokens = filter(bool, tokens)

    return " ".join(tokens) if tokens else ""


def run_partial_templates(
    template_strings: list[str], template_args: dict
) -> list[str]:
    template_args = {k: ("" if v is None else v) for k, v in template_args.items()}
    return [Template(t).safe_substitute(template_args) for t in template_strings]


# def run_templates_to_str(template_str_or_list: str | list[str], template_args: dict):
#     template_str_list = (
#         [template_str_or_list]
#         if isinstance(template_str_or_list, str)
#         else list(template_str_or_list)
#     )

#     template_args = {k: ("" if v is None else v) for k, v in template_args.items()}
#     cmd_tokens = [Template(t).substitute(template_args) for t in template_str_list]
#     return tokens_to_str(*cmd_tokens)


class BaseCmd(ABC):
    def __init__(
        self,
        parent: "BaseCmd",
        template_str_or_list: str | list[str],
        template_args=None,
    ) -> None:
        self.__parent = parent
        self.__template_strings = (
            [template_str_or_list]
            if isinstance(template_str_or_list, str)
            else list(template_str_or_list)
        )
        self._template_args = template_args if template_args else {}

    def _convert(self, *suffix_templates: str) -> str:
        template_strings = [*self.__template_strings, *suffix_templates]
        partials = run_partial_templates(template_strings, self._template_args)
        return self.__parent._convert(*partials) if self.__parent else partials

    def __str__(self) -> str:
        raise ValueError("Unable to convert to string")


class RootCmd(BaseCmd):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(None, *args, **kwargs)


class SubCmd(BaseCmd, ABC):
    def __init__(self, parent: BaseCmd | str, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)


class EndCmd(BaseCmd):
    def __str__(self) -> str:
        return tokens_to_str(*self._convert())
