from pathlib import Path
import json

DEFAULT_CONFIG = {"entrypoint": "pack.py", "generated_dir": "__generated__"}
DEFAULT_NAME = "mcpy_config.json"


def find_config_path(datapack_path: Path, use_default=False) -> Path:
    """Find the path to an existing config file in a datapack directory

    Args:
        datapack_path: path to the root of the datapack
        use_default: if the config file is not found, return the default path
    Returns:
        Path to config file or None if not found
    """
    config_file_name = "mcpy_config.json"
    config_file_path = datapack_path / "src" / DEFAULT_NAME if use_default else None
    if (p := datapack_path / config_file_name).is_file():
        config_file_path = p
    elif (p := datapack_path / "src" / config_file_name).is_file():
        config_file_path = p
    # TODO lastly check inside module folder with glob

    return config_file_path


def write_config(config_path: Path, content: dict):
    """Write a config dict to a path

    Args:
        config_path: Path to write the config file
        content: Dict representation of config options to write to the file

    """
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(content, indent=True, sort_keys=True))


def load_config(config_path: Path, nonexistent_ok=False) -> dict:
    config = DEFAULT_CONFIG.copy()
    if config_path.is_file():
        with open(config_path) as f:
            config = __merge(json.load(f), config)
    return config

def load_default_config() -> dict:
    return DEFAULT_CONFIG.copy()

def load_config_for_datapack(datapack_path: Path) -> dict:
    config = DEFAULT_CONFIG.copy()
    config_file_path = find_config_path(datapack_path)

    if config_file_path:
        with open(config_file_path) as f:
            config = __merge(json.load(f), config)
    return config


def __merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            __merge(value, node)
        else:
            destination[key] = value

    return destination
