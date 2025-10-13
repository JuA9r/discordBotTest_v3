import configparser
import os
from pathlib import Path


class ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.ini_file_path = "../discord_bot/bot.ini"
        self.config.read(self.ini_file_path, encoding="utf-8")

    def read_config(self):
        return self.config.read(self.ini_file_path, encoding="utf-8")

    def get_token(self):
        if not self.read_config():
            print("No config file found")
            return None
        else:
            print()
            try:
                _token = self.config["DISCORD"]["DISCORD_TOKEN"]
                return _token
            except KeyError as e:
                print(f"KeyError: {e} is not found in config file")
            except Exception as e:
                print(f"Exception: {e}")


if __name__ == "__main__":
    config_manager = ConfigManager()
    token = config_manager.get_token()
    print(f"read to {config_manager.read_config()[0]}")
    print(token[:5])