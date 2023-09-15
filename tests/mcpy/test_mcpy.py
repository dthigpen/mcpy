from mcpy import *
from mcpy.mcpy import build
from mcpy.cmd import *
from mcpy.cmd.nbt import *
from pathlib import Path
import json
from textwrap import dedent

def create_datapack_env(root_dir: Path):
    mcmeta = root_dir / "pack.mcmeta"
    mcmeta.write_text('{"pack": {"pack_format": 10,"description": ""}}')


def test_json_files(tmp_path):
    create_datapack_env(tmp_path)
    expected_json_file_content_dict = {"values": ["test:foo", "test:bar"]}
    @datapack
    def builder():
        with namespace("py.test"):
            # raw json file
            with directory("functions"):
                @json_file(category="tags")
                def my_json():
                    yield expected_json_file_content_dict

            # functions tag file
            @functions
            def my_functions():
                yield expected_json_file_content_dict

            # blocks tag file
            @blocks
            def my_blocks():
                yield expected_json_file_content_dict
            
            # items tag file
            @items
            def my_items():
                yield expected_json_file_content_dict


    build(builder, tmp_path)

    file_path = tmp_path / "data/py.test/tags/functions/my_json.json"
    assert file_path.is_file() is True
    actual_content_dict = json.loads(file_path.read_text())
    assert json.dumps(expected_json_file_content_dict) == json.dumps(
        actual_content_dict
    )

    file_path = tmp_path / "data/py.test/tags/functions/my_functions.json"
    assert file_path.is_file() is True
    actual_content_dict = json.loads(file_path.read_text())
    assert json.dumps(expected_json_file_content_dict) == json.dumps(
        actual_content_dict
    )

    file_path = tmp_path / "data/py.test/tags/blocks/my_blocks.json"
    actual_content_dict = json.loads(file_path.read_text())
    assert json.dumps(expected_json_file_content_dict) == json.dumps(
        actual_content_dict
    )

    file_path = tmp_path / "data/py.test/tags/items/my_items.json"
    actual_content_dict = json.loads(file_path.read_text())
    assert json.dumps(expected_json_file_content_dict) == json.dumps(
        actual_content_dict
    )

def test_mcfunction_file(tmp_path):
    create_datapack_env(tmp_path)

    expected_mcfunction_content = dedent('''\
        # Built with mcpy (https://github.com/dthigpen/mcpy)

        say hello
        ''')
    
    @datapack
    def builder():
        with namespace("py.test"):
            @mcfunction(name='myfile')
            def _myfile():
                yield "say hello"

            @mcfunction
            def myfile2():
                yield ("say hello")

            @mcfunction
            def myfile4():
                yield 'say cmd 1'
                myfile2()
                yield f'execute run function {myfile2}'
            
            # different namespace
            with namespace("py.dev"):
                @mcfunction
                def say_hi():
                    yield "say hello"

    build(builder, tmp_path)

    # data and namespace dirs
    assert tmp_path.joinpath("data", "py.test").is_dir()

    # mcfunction files
    file_path = tmp_path / "data/py.test/functions/myfile.mcfunction"
    assert file_path.read_text() == expected_mcfunction_content
    # check the non yielding version
    file_path = tmp_path / "data/py.test/functions/myfile2.mcfunction"
    assert file_path.read_text() == expected_mcfunction_content

    file_path = tmp_path.joinpath("data", "py.test", "functions", "myfile4.mcfunction")
    expected_execute_content = dedent('''\
            # Built with mcpy (https://github.com/dthigpen/mcpy)
            
            say cmd 1
            function py.test:myfile2
            execute run function py.test:myfile2
            ''')
    assert file_path.read_text() == expected_execute_content
    file_path = tmp_path / "data/py.dev/functions/say_hi.mcfunction"
    assert file_path.read_text() == expected_mcfunction_content

def test_mcfunction_execute(tmp_path):
    @datapack
    def builder():
        with namespace("py.test"):
            # mcfunction with execute
            @mcfunction
            def myfile3():
                yield 'say before execute'
                # below default inline limit
                with execute('if score $holder obj matches 1'):
                    yield 'say cmd 1'
                    yield 'say cmd 2'
                # at default inline limit
                with execute('if score $holder obj matches 1'):
                    yield 'say cmd 1'
                    yield 'say cmd 2'
                    yield 'say cmd 3'
                # over default inline limit, move to another function
                with execute('if score $holder obj matches 1'):
                    yield 'say cmd 1'
                    yield 'say cmd 2'
                    yield 'say cmd 3'
                    yield 'say cmd 4'
                    yield 'say cmd 5'

    build(builder, tmp_path)
    # check execute was properly handled
    file_path = tmp_path / "data/py.test/functions/myfile3.mcfunction"
    expected_execute_content = dedent('''\
        # Built with mcpy (https://github.com/dthigpen/mcpy)
        
        say before execute
        execute if score $holder obj matches 1 run say cmd 1
        execute if score $holder obj matches 1 run say cmd 2
        execute if score $holder obj matches 1 run say cmd 1
        execute if score $holder obj matches 1 run say cmd 2
        execute if score $holder obj matches 1 run say cmd 3
        execute if score $holder obj matches 1 run function py.test:__generated__/myfile3_0
        ''')
    assert file_path.read_text() == expected_execute_content
    file_path = tmp_path / "data/py.test/functions/__generated__/myfile3_0.mcfunction"
    expected_execute_content = dedent('''\
            # Built with mcpy (https://github.com/dthigpen/mcpy)
            
            say cmd 1
            say cmd 2
            say cmd 3
            say cmd 4
            say cmd 5
            ''')
def test_cmd_common():
    assert str(Selector('@z').where('tag','py.test')) == '@z[tag=py.test]'
    assert str(CurrentEntity.where('tag','py.test').where('scores',{'py.score':'1..3'})) == '@s[tag=py.test,scores={py.score=1..3}]'

def test_cmd_tag():
    assert str(Tag('py.foo')) == 'py.foo'
    assert str(Tag('py.foo').negate()) == '!py.foo'
    assert str(~Tag('py.foo')) == '!py.foo'
    assert str(~(~Tag('py.foo'))) == 'py.foo'
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
    assert str(nbt.key('ingredient').where(123)) == 'this.ingredient[123]'
    obj = NbtObj({'foo':'bar','123':'aaa'})
    assert str(obj) == '{"foo": "bar", "123": "aaa"}'
