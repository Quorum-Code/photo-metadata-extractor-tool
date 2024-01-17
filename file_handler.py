import configparser
import json
import os
import codecs
from pathlib import Path

DEFAULT_DB_FOLDER_PATH = Path.home().joinpath("pmet")
DEFAULT_DB_FILE_PATH = Path.home().joinpath("pmet/pmet-data.json")
DEFAULT_SECRETS_FILE_PATH = Path.home().joinpath("pmet/.secrets")

DEFAULT_SETTINGS = {
    "style": "system"
}

DEFAULT_CONFIGURATION = {
    "token": {
        "headers": {

        },
        "parameters": {

        }
    },
    "query": {
        "headers": {

        },
        "parameters": {

        }
    }
}

DEFAULT_SECRETS = {
    "client_id": "",
    "client_secret": ""
}

DEFAULT_DATA = {
    "settings": DEFAULT_SETTINGS,
    "configuration": DEFAULT_CONFIGURATION
}


class FileHandler:
    def __init__(self):
        # File paths
        self.pmet_folder_path: Path = DEFAULT_DB_FOLDER_PATH
        self.pmet_setting_file_path: Path = DEFAULT_DB_FILE_PATH
        self.pmet_secrets_file_path: Path = DEFAULT_SECRETS_FILE_PATH
        self.__indent = 4

        self.settings: dict = {}

        # Initialize all files
        self.__init_pmet_folder()
        self.__init_pmet_data_json()
        self.__init_secrets_file()

        # Read files
        # self.load_settings()
        self.load_secrets()

        # Load data as dict
        self.__json_data: dict = self.__load_json()

    def load_settings(self):
        try:
            with self.pmet_setting_file_path.open("r", encoding="utf-8") as f:
                self.settings = json.loads(f.read())
            return True
        except FileNotFoundError:
            self.settings = DEFAULT_SETTINGS
            return False
        except json.JSONDecodeError:
            return False

    def update_settings(self):
        try:
            with self.pmet_setting_file_path.open("w") as f:
                f.write((json.dumps(self.settings)))
                f.close()
        except FileNotFoundError:
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

    def save_style(self, style: str):
        self.__json_data["settings"]["style"] = style
        self.__save_json()

    def get_settings(self) -> dict:
        return self.__json_data["settings"]

    def get_setting(self) -> str:
        pass

    def get_configuration(self) -> dict:
        return self.__json_data["configuration"]

    def get_secrets(self) -> dict:
        pass

    def __init_pmet_folder(self):
        # Check if settings folder exists
        if not self.pmet_folder_path.exists():
            try:
                self.pmet_folder_path.mkdir(parents=True, exist_ok=False)
            except OSError:
                return False
        return True

    def __init_pmet_data_json(self):
        # Check if settings json exists
        if not self.pmet_setting_file_path.exists():
            # Try to create settings json
            try:
                with self.pmet_setting_file_path.open("w") as f:
                    default_data = {"settings": DEFAULT_SETTINGS, "configuration": DEFAULT_CONFIGURATION}
                    f.write(json.dumps(default_data, indent=self.__indent))
                # self.pmet_setting_file_path.write_text(json.dumps(DEFAULT_SETTINGS))
            except FileNotFoundError:
                return False
            except OSError:
                return False
        return True

    def __init_secrets_file(self):
        if not self.pmet_secrets_file_path.exists():
            try:
                with self.pmet_secrets_file_path.open("wb") as f:
                    f.write(codecs.encode(bytes(f"{DEFAULT_SECRETS}", "utf-8"), "hex"))
            except FileNotFoundError:
                return False
            except OSError:
                return False
        return True

    def __load_json(self, has_failed=False) -> dict:
        """
        Loads json_data from "pmet/pmet-data.json"

        :param has_failed: Flag to cancel loading if repeated failure after attempting to restore data.
        :return:
        """

        json_data = {}
        try:
            with open(self.pmet_setting_file_path) as f:
                json_data = json.loads(f.read())
        except json.JSONDecodeError:
            # File empty
            self.__restore_default_data()
            if not has_failed:
                return self.__load_json(has_failed=True)
            # Abort loading from file, load default
            else:
                return DEFAULT_DATA
        return json_data

    def __restore_default_data(self):
        print("RESTORING JSON DATA")
        json_data = DEFAULT_DATA

        with open(self.pmet_setting_file_path, "w") as f:
            f.write(json.dumps(json_data, indent=self.__indent))

        return

    def __save_json(self):
        with open(self.pmet_setting_file_path, "w") as f:
            f.write(json.dumps(self.__json_data, indent=self.__indent))


def main():
    fh = FileHandler()


if __name__ == "__main__":
    main()
