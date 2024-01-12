import configparser
import json
import os
import codecs

from pathlib import Path

DEFAULT_DB_FOLDER_PATH = Path.home().joinpath("pmet")
DEFAULT_DB_FILE_PATH = Path.home().joinpath("pmet/settings.json")
DEFAULT_SECRETS_FILE_PATH = Path.home().joinpath("pmet/.secrets")

DEFAULT_SETTINGS = {
    "style": "system"
}

DEFAULT_SECRETS = {
    "client_id": "",
    "client_secret": ""
}


class FileHandler:
    def __init__(self):
        # File paths
        self.pmet_folder_path: Path = DEFAULT_DB_FOLDER_PATH
        self.pmet_setting_file_path: Path = DEFAULT_DB_FILE_PATH
        self.pmet_secrets_file_path: Path = DEFAULT_SECRETS_FILE_PATH

        self.settings: dict = {}

        # Initialize all files
        self.init_pmet_folder()
        self.init_settings_json()
        self.init_secrets_file()

        # Read files
        self.load_settings()
        self.load_secrets()

    def init_pmet_folder(self):
        # Check if settings folder exists
        if not self.pmet_folder_path.exists():
            try:
                self.pmet_folder_path.mkdir(parents=True, exist_ok=False)
            except OSError:
                return False
        return True

    def init_settings_json(self):
        # Check if settings json exists
        if not self.pmet_setting_file_path.exists():
            # Try to create settings json
            try:
                with self.pmet_setting_file_path.open("w") as f:
                    f.write(json.dumps(DEFAULT_SETTINGS))
                self.pmet_setting_file_path.write_text(json.dumps(DEFAULT_SETTINGS))
            except FileNotFoundError:
                return False
            except OSError:
                return False
        return True

    def load_settings(self):
        try:
            with self.pmet_setting_file_path.open("r", encoding="utf-8") as f:
                self.settings = json.loads(f.read())
            return True
        except FileNotFoundError:
            self.settings = DEFAULT_SETTINGS
            return False

    def update_settings(self):
        try:
            with self.pmet_setting_file_path.open("w") as f:
                f.write((json.dumps(self.settings)))
                f.close()
        except FileNotFoundError:
            return False
        return True

    def init_secrets_file(self):
        if not self.pmet_secrets_file_path.exists():
            try:
                with self.pmet_secrets_file_path.open("wb") as f:
                    f.write(codecs.encode(bytes(f"{DEFAULT_SECRETS}", "utf-8"), "hex"))
            except FileNotFoundError:
                return False
            except OSError:
                return False
        return True

    def load_secrets(self):
        pass

    def initialize_secrets(self):
        pass

    def save_client_id(self):
        pass

    def save_client_secret(self):
        pass

    def save_style_default(self):
        pass


def main():
    fh = FileHandler()


if __name__ == "__main__":
    main()
