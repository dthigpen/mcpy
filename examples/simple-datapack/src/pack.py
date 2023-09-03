from mcpy import *
from mcpy.cmd import *


@datapack
def simple_pack():
    with namespace("dt.simple"):
        with directory("api/greeting"):

            @mcfunction
            def hello():
                yield "say Hello"
                yield "say There!!"

            # or with multiple commands in one str:
            @mcfunction
            def morning():
                yield """\
                say Good
                say Morning!
                """

            # or as a list
            @mcfunction
            def all():
                yield [
                    "say Good evening",
                    "say Good afternoon!",
                    "say Good night!",
                ]
