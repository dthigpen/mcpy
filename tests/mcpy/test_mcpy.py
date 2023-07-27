from mcpy import *
from mcpy.mcpy import build
from mcpy.cmd import *
from mcpy.cmd.nbt import *
from pathlib import Path
import json


def create_datapack_env(root_dir: Path):
    mcmeta = root_dir / "pack.mcmeta"
    mcmeta.write_text('{"pack": {"pack_format": 10,"description": ""}}')


def test_file_creations(tmp_path):
    create_datapack_env(tmp_path)
    expected_mcfunction_content = (
        "# Built with mcpy (https://github.com/dthigpen/mcpy)\n" "\n" f"say hello" "\n"
    )
    expected_json_file_content_dict = {"values": ["test:foo", "test:bar"]}
    @datapack
    def builder():
        with namespace("py.test"):
            # mcfunction
            with mcfunction("myfile"):
                yield "say hello"

            # mcfunction
            with mcfunction("myfile2"):
                yield ("say hello")

            # mcfunction with execute
            with mcfunction("myfile3"):
                yield 'say before execute'

                with execute('if score $holder obj matches 1'):
                    yield 'say cmd 1'
                    yield 'say cmd 2'

                with execute('if score $holder obj matches 1'):
                    yield 'say cmd 1'
                    yield 'say cmd 2'
                    yield 'say cmd 3'
                    
                with execute('if score $holder obj matches 1'):
                    yield 'say cmd 1'
                    yield 'say cmd 2'
                    yield 'say cmd 3'
                    yield 'say cmd 4'
            # raw json file
            with dir("functions"):
                with json_file("my_json", category="tags"):
                    yield expected_json_file_content_dict
            # blocks tag file
            with blocks("my_blocks"):
                yield expected_json_file_content_dict

            # different namespace
            with namespace("py.dev"):
                with mcfunction("say_hi"):
                    yield "say hello"

    build(builder, tmp_path)
    # data and namespace dirs
    assert tmp_path.joinpath("data", "py.test").is_dir()

    # mcfunction files
    file_path = tmp_path.joinpath("data", "py.test", "functions", "myfile.mcfunction")
    assert file_path.read_text() == expected_mcfunction_content
    # check the non yielding version
    file_path = tmp_path.joinpath("data", "py.test", "functions", "myfile2.mcfunction")
    assert file_path.read_text() == expected_mcfunction_content
    # check execute was properly handled
    file_path = tmp_path.joinpath("data", "py.test", "functions", "myfile3.mcfunction")
    expected_execute_content = (
        "# Built with mcpy (https://github.com/dthigpen/mcpy)\n"
        "\n"
        f"say before execute\n"
        f"execute if score $holder obj matches 1 run say cmd 1\n"
        f"execute if score $holder obj matches 1 run say cmd 2\n"
        f"execute if score $holder obj matches 1 run say cmd 1\n"
        f"execute if score $holder obj matches 1 run say cmd 2\n"
        f"execute if score $holder obj matches 1 run say cmd 3\n"
        f"execute if score $holder obj matches 1 run function py.test:__generated__/gen_myfile32\n"
    )
    assert file_path.read_text() == expected_execute_content
    file_path = tmp_path.joinpath("data", "py.test", "functions", "__generated__","gen_myfile32.mcfunction")
    expected_execute_content = (
            "# Built with mcpy (https://github.com/dthigpen/mcpy)\n"
            "\n"
            f"say cmd 1\n"
            f"say cmd 2\n"
            f"say cmd 3\n"
            f"say cmd 4\n"
        )
    assert file_path.read_text() == expected_execute_content
    file_path = tmp_path.joinpath("data", "py.dev", "functions", "say_hi.mcfunction")
    assert file_path.read_text() == expected_mcfunction_content

    file_path = tmp_path.joinpath(
        "data", "py.test", "tags", "functions", "my_json.json"
    )
    assert file_path.is_file() is True
    actual_content_dict = json.loads(file_path.read_text())
    assert json.dumps(expected_json_file_content_dict) == json.dumps(
        actual_content_dict
    )

    file_path = tmp_path.joinpath("data", "py.test", "tags", "blocks", "my_blocks.json")
    actual_content_dict = json.loads(file_path.read_text())
    assert json.dumps(expected_json_file_content_dict) == json.dumps(
        actual_content_dict
    )


def test_nbt():
    assert str(Bool(True)) == 'true'
    assert str(Bool(False)) == 'false'
    assert str(Short(1)) == '1s'
    assert str(Float(123.4)) == '123.4f'
    assert str(Byte(123)) == '123b'
    assert str(Str('Hello!')) == '"Hello!"'
    assert str(Str('Hello "Human"!')) == '"Hello \\"Human\\"!"'
    # obj = NbtObj({'foo':'bar','123':'aaa'})
    # assert str(obj) == '{"foo": "bar", "123": "aaa"}'
    # obj = NbtObj({'foo':True,'123':'aaa'})
    # assert str(obj) == '{"foo": true, "123": "aaa"}'
    obj = NbtObj({'foo':Byte(123),'123':'aaa'})
    assert str(obj) == '{"foo": 123b, "123": "aaa"}'
    # obj = NbtObj({'foo':{"inner":Float(12.3)},'123':'aaa'})
    # assert str(obj) == '{"foo": {"inner": 12.3f}, "123": "aaa"}'
    

    nbt = NbtPath('this')
    assert str(nbt) == 'this'
    assert str(nbt.key('ingredient')) == 'this.ingredient'
    assert str(nbt.key('ingredient').at(123)) == 'this.ingredient[123]'
    obj = NbtObj({'foo':'bar','123':'aaa'})
    assert str(obj) == '{"foo": "bar", "123": "aaa"}'
