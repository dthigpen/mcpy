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
                with pack.mcfunction("morning"):
                    yield """\
                    say Good
                    say Morning!
                    """

                # or as a list
                with pack.mcfunction("all"):
                    yield [
                        "say Good evening",
                        "say Good afternoon!",
                        "say Good night!",
                    ]

    pack.build(builder())

    # ----------------------------------------------------
    pack = Datapack()
    with pack.namespace("dt.simple"):
        with pack.dir("api/greeting"):
            with pack.mcfunction("hello"):
                pack.write("say Hello")
                pack.write("say There!")

            # or with multiple commands in one str:
            with pack.mcfunction("morning"):
                pack.write(
                    """\
                say Good
                say Morning!
                """
                )

            # or as a list
            with pack.mcfunction("all"):
                pack.write(
                    [
                        "say Good evening",
                        "say Good afternoon!",
                        "say Good night!",
                    ]
                )
