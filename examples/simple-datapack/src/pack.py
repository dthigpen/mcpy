from mcpy import *


@datapack
def simple_pack():
    with namespace("dt.simple"):
        with dir("api/greeting"):
            with mcfunction("hello"):
                yield "say Hello"
                yield "say There!!"

            # or with multiple commands in one str:
            with mcfunction("morning"):
                yield """\
                say Good
                say Morning!
                """

            # or as a list
            with mcfunction("all"):
                yield [
                    "say Good evening",
                    "say Good afternoon!",
                    "say Good night!",
                ]
