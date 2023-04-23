import mcpy.cmd.scoreboard as scoreboard
import mcpy.cmd.data as data

def __assert_cmds(expected_str: str, cmd: any):
    assert expected_str == str(cmd)


def test_scoreboard():
    # objectives
    # list
    __assert_cmds(
        "scoreboard objectives list", scoreboard.Scoreboard().objectives().list()
    )

    # add
    __assert_cmds(
        "scoreboard objectives add test.obj dummy",
        scoreboard.Scoreboard().objectives().add("test.obj", "dummy"),
    )
    __assert_cmds(
        "scoreboard objectives add test.obj dummy TEST_OBJ",
        scoreboard.Scoreboard()
        .objectives()
        .add("test.obj", "dummy", display_name="TEST_OBJ"),
    )
    # players
    # set
    expected = "scoreboard players set test.player test.obj 123"
    cmd = scoreboard.Player("test.player", "test.obj").set(123)
    assert expected == str(cmd)
    # set
    expected = "scoreboard players reset test.player test.obj"
    cmd = scoreboard.Player("test.player", "test.obj").reset()
    assert expected == str(cmd)

    # operation =
    expected = (
        "scoreboard players operation test.player test.obj = test.player2 test.obj2"
    )
    cmd = (
        scoreboard.Player("test.player", "test.obj")
        .operation()
        .assign(scoreboard.Player("test.player2", "test.obj2"))
    )
    assert expected == str(cmd)
    # operation +=
    expected = (
        "scoreboard players operation test.player test.obj += test.player2 test.obj2"
    )
    cmd = (
        scoreboard.Player("test.player", "test.obj")
        .operation()
        .add(scoreboard.Player("test.player2", "test.obj2"))
    )
    assert expected == str(cmd)

    # operation -=
    expected = (
        "scoreboard players operation test.player test.obj -= test.player2 test.obj2"
    )
    cmd = (
        scoreboard.Player("test.player", "test.obj")
        .operation()
        .subtract(scoreboard.Player("test.player2", "test.obj2"))
    )
    assert expected == str(cmd)
    # operation *=
    expected = (
        "scoreboard players operation test.player test.obj *= test.player2 test.obj2"
    )
    cmd = (
        scoreboard.Player("test.player", "test.obj")
        .operation()
        .multiply(scoreboard.Player("test.player2", "test.obj2"))
    )
    assert expected == str(cmd)

    # operation /=
    __assert_cmds(
        "scoreboard players operation test.player test.obj /= test.player2 test.obj2",
        scoreboard.Player("test.player", "test.obj")
        .operation()
        .divide(scoreboard.Player("test.player2", "test.obj2")),
    )

    # operation %=
    __assert_cmds(
        "scoreboard players operation test.player test.obj %= test.player2 test.obj2",
        scoreboard.Player("test.player", "test.obj")
        .operation()
        .mod(scoreboard.Player("test.player2", "test.obj2")),
    )

    # operation <
    __assert_cmds(
        "scoreboard players operation test.player test.obj < test.player2 test.obj2",
        scoreboard.Player("test.player", "test.obj")
        .operation()
        .min(scoreboard.Player("test.player2", "test.obj2")),
    )

    # operation >
    __assert_cmds(
        "scoreboard players operation test.player test.obj > test.player2 test.obj2",
        scoreboard.Player("test.player", "test.obj")
        .operation()
        .max(scoreboard.Player("test.player2", "test.obj2")),
    )
    # operation ><
    __assert_cmds(
        "scoreboard players operation test.player test.obj >< test.player2 test.obj2",
        scoreboard.Player("test.player", "test.obj")
        .operation()
        .swap(scoreboard.Player("test.player2", "test.obj2")),
    )

def test_data():
    # storage get,remove,merge
    __assert_cmds('data get storage test.example foopath', data.Storage('test.example','foopath').get())
    __assert_cmds('data remove storage test.example foopath', data.Storage('test.example','foopath').remove())
    __assert_cmds('data merge storage test.example {foo:1b}', data.Storage('test.example','foopath').merge("{foo:1b}"))
    # modify
