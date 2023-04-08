from mcpy import Datapack


if __name__ == "__main__":
    pack = Datapack()

    def builder():
        with pack.namespace("dt.simple"):

            with pack.dir("api/greeting"):
                with pack.mcfunction("hello"):
                    yield "say Hello"
                    yield "say There!"
                # or with multiple commands in one str:
                with pack.mcfunction("hello"):
                    yield """\
                    say Good
                    say Morning!
                    """

    pack.build(builder())

    # Alternatively this can be expressed without yields such as below
    # for the exact same result using the context managers "as" value
    pack = Datapack()
    with pack.namespace("dt.simple"):

        with pack.dir("api/greeting"):
            with pack.mcfunction("hello") as write:
                write("say Hello")
                write("say There!")
            # or with multiple commands in one str:
            with pack.mcfunction("morning") as write:
                write(
                    """\
                say Good
                say Morning!
                """
                )
