from mcpy.cmd import *


def __assert_cmds(expected_str: str, cmd: any):
    assert expected_str == str(cmd)


def test_scoreboard():
    # objectives
    # list
    __assert_cmds("scoreboard objectives list", Scoreboard.objectives().list())

    # add
    __assert_cmds(
        "scoreboard objectives add test.obj dummy",
        Scoreboard.objectives().add("test.obj", "dummy"),
    )
    __assert_cmds(
        "scoreboard objectives add test.obj dummy TEST_OBJ",
        Scoreboard.objectives().add("test.obj", "dummy", display_name="TEST_OBJ"),
    )
    # players
    # set
    __assert_cmds(
        "scoreboard players set test.player test.obj 123",
        cmd=Scoreboard.Player("test.player", "test.obj").set(123),
    )
    # set
    __assert_cmds(
        "scoreboard players reset test.player test.obj",
        Scoreboard.Player("test.player", "test.obj").reset(),
    )

    # operation =
    __assert_cmds(
        "scoreboard players operation test.player test.obj = test.player2 test.obj2",
        Scoreboard.Player("test.player", "test.obj")
        .operation()
        .assign(Scoreboard.Player("test.player2", "test.obj2")),
    )
    # operation +=
    __assert_cmds(
        "scoreboard players operation test.player test.obj += test.player2 test.obj2",
        Scoreboard.Player("test.player", "test.obj")
        .operation()
        .add(Scoreboard.Player("test.player2", "test.obj2")),
    )

    # operation -=
    __assert_cmds(
        "scoreboard players operation test.player test.obj -= test.player2 test.obj2",
        Scoreboard.Player("test.player", "test.obj")
        .operation()
        .subtract(Scoreboard.Player("test.player2", "test.obj2")),
    )
    # operation *=
    __assert_cmds(
        "scoreboard players operation test.player test.obj *= test.player2 test.obj2",
        Scoreboard.Player("test.player", "test.obj")
        .operation()
        .multiply(Scoreboard.Player("test.player2", "test.obj2")),
    )

    # operation /=
    __assert_cmds(
        "scoreboard players operation test.player test.obj /= test.player2 test.obj2",
        Scoreboard.Player("test.player", "test.obj")
        .operation()
        .divide(Scoreboard.Player("test.player2", "test.obj2")),
    )

    # operation %=
    __assert_cmds(
        "scoreboard players operation test.player test.obj %= test.player2 test.obj2",
        Scoreboard.Player("test.player", "test.obj")
        .operation()
        .mod(Scoreboard.Player("test.player2", "test.obj2")),
    )

    # operation <
    __assert_cmds(
        "scoreboard players operation test.player test.obj < test.player2 test.obj2",
        Scoreboard.Player("test.player", "test.obj")
        .operation()
        .min(Scoreboard.Player("test.player2", "test.obj2")),
    )

    # operation >
    __assert_cmds(
        "scoreboard players operation test.player test.obj > test.player2 test.obj2",
        Scoreboard.Player("test.player", "test.obj")
        .operation()
        .max(Scoreboard.Player("test.player2", "test.obj2")),
    )
    # operation ><
    __assert_cmds(
        "scoreboard players operation test.player test.obj >< test.player2 test.obj2",
        Scoreboard.Player("test.player", "test.obj")
        .operation()
        .swap(Scoreboard.Player("test.player2", "test.obj2")),
    )


def test_data():
    # storage get,remove,merge
    __assert_cmds(
        "data get storage test.example foopath",
        Data.Storage("test.example", "foopath").get(),
    )
    __assert_cmds(
        "data remove storage test.example foopath",
        Data.Storage("test.example", "foopath").remove(),
    )
    __assert_cmds(
        "data merge storage test.example {foo:1b}",
        Data.Storage("test.example", "foopath").merge("{foo:1b}"),
    )
    # modify
