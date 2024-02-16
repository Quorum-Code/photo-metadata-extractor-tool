import configparser
import json
import os
import codecs
import copy
import sys
from pathlib import Path

DEFAULT_DB_FOLDER_PATH = Path.home().joinpath("pmet")
DEFAULT_DB_FILE_PATH = Path.home().joinpath("pmet/pmet-data.json")
DEFAULT_SECRETS_FILE_PATH = Path.home().joinpath("pmet/.secrets")

DEFAULT_SETTINGS = {
    "program_path": "",
    "style": "system"
}

DEFAULT_CONFIGURATION = {
    "token": {
        "url": "https://oauth.oclc.org/token",
        "headers": {
            "accept": "application/json"
        },
        "body": {
            "grant_type": "client_credentials",
            "scope": "wcapi",
            "context": 285
        }
    },
    "query": {
        "url": "https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs",
        "headers": {
            "accept": "application/json"
        },
        "parameters": {
            "q": "",
            "heldByInstitutionID": "128807,45266",
            "itemType": "",
            "itemSubType": "",
            "retentionCommitments": "false",
            "facets": "content",
            "groupRelatedEditions": "false",
            "groupVariantRecords": "false",
            "orderBy": "bestMatch",
            "offset": 1,
            "limit": 10

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

        # Load secrets as dict
        self.__secrets: dict = self.__load_secrets()

    def save_data(self, data: dict):
        with self.pmet_setting_file_path.open("w") as f:
            f.write(json.dumps(data, indent=self.__indent))

    def get_program_path(self) -> str:
        if "program_path" in self.__json_data["settings"].keys() and self.__json_data["settings"]["program_path"] != "":
            return self.__json_data["settings"]["program_path"]
        return None

    def test_print(self, text):
        print(f"File handler function called with: {text}")

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

    def get_style(self) -> str:
        return self.__json_data["settings"]["style"]

    def get_settings(self) -> dict:
        return copy.deepcopy(self.__json_data["settings"])

    def get_setting(self, key: str) -> str:
        if key in self.__json_data:
            return self.__json_data[key]
        else:
            return ""

    def get_configuration(self) -> dict:
        return self.__json_data["configuration"]

    def get_secrets(self) -> dict:
        pass

    # todo: find best practice for copying dictionaries from an object
    def get_token_headers(self) -> dict:
        return copy.deepcopy(self.__json_data["configuration"]["token"]["headers"])

    def get_token_body(self) -> dict:
        return copy.deepcopy(self.__json_data["configuration"]["token"]["body"])

    def get_query_headers(self) -> dict:
        return copy.deepcopy(self.__json_data["configuration"]["query"]["headers"])

    def get_query_parameters(self) -> dict:
        return copy.deepcopy(self.__json_data["configuration"]["query"]["parameters"])

    def set_config(self, token_headers: str, token_body: str, query_headers: str, query_parameters: str) -> bool:
        token_headers = self.__json_form_str(token_headers)
        token_body = self.__json_form_str(token_body)
        query_headers = self.__json_form_str(query_headers)
        query_parameters = self.__json_form_str(query_parameters)

        new_dict = {
            "token": {},
            "query": {}
        }

        try:
            new_dict["token"]["headers"] = json.loads(token_headers)
            new_dict["token"]["body"] = json.loads(token_body)
            new_dict["query"]["headers"] = json.loads(query_headers)
            new_dict["query"]["parameters"] = json.loads(query_parameters)

            self.__set_configuration(new_dict)
            self.__save_json()

            return True

        except json.JSONDecodeError:
            # load the default configs
            # throw error window saying json syntax error
            return False

    def set_secrets(self, client_id: str, client_secret: str):
        self.__save_secrets(client_id, client_secret)
        self.__secrets = self.__load_secrets()

        print(f"Secrets! {self.__secrets}")

    def load_default_config(self):
        self.__json_data["configuration"] = DEFAULT_CONFIGURATION

    def __json_form_str(self, text: str) -> str:
        return text.replace('\'', '\"')

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
                    self.__init_program_path(default_data)
                    f.write(json.dumps(default_data, indent=self.__indent))
                # self.pmet_setting_file_path.write_text(json.dumps(DEFAULT_SETTINGS))
            except FileNotFoundError:
                return False
            except OSError:
                return False
        return True

    def __init_program_path(self, default_data: dict):
        if os.getcwd().endswith("\\photo-metadata-extractor-tool") and os.path.exists("gui") and os.path.exists("oclc"):
            default_data["settings"]["program_path"] = os.getcwd()
            self.save_data(default_data)
        else:
            print("The program must be started at its directory to be initialized."
                  " (After the first run it should be able to be run from any directory.)")
            sys.exit("ERROR: Bad pwd")

    def __init_secrets_file(self):
        if not self.pmet_secrets_file_path.exists():
            try:
                with self.pmet_secrets_file_path.open("wb") as f:
                    # no longer warning highlighted?? ok....
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

        # TODO: verify integrity of stored json data

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

        if "program_path" not in json_data["settings"].keys() or json_data["settings"]["program_path"] == "":
            print("No program path")
            self.__init_program_path(json_data)
        else:
            print("has program path")

        return json_data

    def __restore_default_data(self):
        json_data = DEFAULT_DATA
        self.__init_program_path(json_data)

        # todo: archive old data before overwriting... i.e save as pmet-data-1-17-2024.json

        with open(self.pmet_setting_file_path, "w") as f:
            f.write(json.dumps(json_data, indent=self.__indent))

        return

    def __set_configuration(self, new_config: dict):
        self.__json_data["configuration"] = new_config

    def __save_json(self):
        print("Saving JSON...")
        print(self.__json_data)
        with open(self.pmet_setting_file_path, "w") as f:
            f.write(json.dumps(self.__json_data, indent=self.__indent))

    def __save_secrets(self, client_id, client_secret):
        new_secrets = {"client_id": client_id, "client_secret": client_secret}

        with open(self.pmet_secrets_file_path, "wb") as f:
            f.write(codecs.encode(bytes(f"{new_secrets}", "utf-8"), "hex"))

    def __load_secrets(self) -> dict:
        with open(self.pmet_secrets_file_path, "rb") as f:
            text = f"{codecs.decode(f.read(), 'hex').decode()}"
            text = text.replace('\'', '\"')
            return json.loads(text)


def main():
    fh = FileHandler()


if __name__ == "__main__":
    main()
