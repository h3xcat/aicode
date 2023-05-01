import configparser
from pathlib import Path


def save_config(config: configparser.ConfigParser, config_path: Path):
    with open(config_path, "w") as configfile:
        config.write(configfile)


def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config_path = Path("./settings.ini")
    config.read(config_path)

    if "Settings" not in config:
        config["Settings"] = {"model": "gpt-3.5-turbo"}

    return config, config_path
