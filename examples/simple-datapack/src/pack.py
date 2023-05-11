from mcpy import *


@datapack
def simple_pack(ctx: Context):
    with namespace(ctx, "dt.simple"):
        with dir(ctx, "api/greeting"):
            with mcfunction(ctx, "hello"):
                yield "say Hello"
                yield "say There!!"

            # or with multiple commands in one str:
            with mcfunction(ctx, "morning"):
                yield """\
                say Good
                say Morning!
                """

            # or as a list
            with mcfunction(ctx, "all"):
                yield [
                    "say Good evening",
                    "say Good afternoon!",
                    "say Good night!",
                ]
