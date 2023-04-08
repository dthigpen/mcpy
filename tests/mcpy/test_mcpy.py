from mcpy import Datapack, DEFAULT_HEADER_MSG
from pathlib import Path
import json


def create_datapack_env(root_dir: Path):
    mcmeta = root_dir / "pack.mcmeta"
    mcmeta.write_text('{"pack": {"pack_format": 10,"description": ""}}')


def test_file_creations(tmp_path):
    create_datapack_env(tmp_path)
    pack = Datapack(base_dir=tmp_path)
    expected_mcfunction_content = (
        "# Built with mcpy (https://github.com/dthigpen/mcpy)\n" "\n" f"say hello" "\n"
    )
    expected_json_file_content_dict = {"values": ["test:foo", "test:bar"]}

    # TODO test no-yielding style
    def builder():
        with pack.namespace("py.test"):
            # mcfunction
            with pack.mcfunction("myfile") as f:
                yield "say hello"

            # raw json file
            with pack.dir("functions"):
                with pack.json_file("my_json", category="tags"):
                    yield expected_json_file_content_dict
            # blocks tag file
            with pack.blocks("my_blocks"):
                yield expected_json_file_content_dict

    pack.build(builder())
    mcfunction_path = tmp_path.joinpath(
        "data", "py.test", "functions", "myfile.mcfunction"
    )
    assert mcfunction_path.is_file() is True
    assert mcfunction_path.read_text() == expected_mcfunction_content

    json_file_path = tmp_path.joinpath(
        "data", "py.test", "tags", "functions", "my_json.json"
    )
    assert json_file_path.is_file() is True
    actual_content_dict = json.loads(json_file_path.read_text())
    assert json.dumps(expected_json_file_content_dict) == json.dumps(
        actual_content_dict
    )

    json_file_path = tmp_path.joinpath(
        "data", "py.test", "tags", "blocks", "my_blocks.json"
    )
    assert json_file_path.exists() is True
    actual_content_dict = json.loads(json_file_path.read_text())
    assert json.dumps(expected_json_file_content_dict) == json.dumps(
        actual_content_dict
    )
