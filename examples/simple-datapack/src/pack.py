from mcpy import *


@datapack
def simple_pack():
    with namespace("dt.simple"):
        with directory("api/greeting"):
            with mcfunction_old("hello"):
                yield "say Hello"
                yield "say There!!"

            # or with multiple commands in one str:
            with mcfunction_old("morning"):
                yield """\
                say Good
                say Morning!
                """

            # or as a list
            with mcfunction_old("all"):
                yield [
                    "say Good evening",
                    "say Good afternoon!",
                    "say Good night!",
                ]
