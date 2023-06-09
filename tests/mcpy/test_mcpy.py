from mcpy import *
from mcpy.mcpy import build
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
