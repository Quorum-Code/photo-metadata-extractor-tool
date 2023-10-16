import requests
import json
import base64
import configparser


class OCLCSession:
    def __init__(self, config_file: str):
        # Config settings
        self.config = configparser.ConfigParser()
        self.config.sections()
        self.config.read(config_file)

        # URLs
        self.token_url = self.config['URLS']['token_url']
        self.auth_url = self.config['URLS']['auth_url']
        self.metadata_service_url = self.config['URLS']['metadata_service_url']

        # Auth-token setup
        self.signature = self.get_signature()
        self.token_headers = self.get_auth_headers()
        self.token_body = self.get_auth_body()

        # Request Auth token
        self.token = self.get

    def get_signature(self) -> str:
        # Get credentials
        secrets = open(self.config['Directories']['secrets'], "r")
        client_id = secrets.readline()
        client_secret = secrets.readline()
        secrets.close()

        # Unsigned credentials
        credentials = f"{client_id}:{client_secret}"
        credentials = credentials.replace("\n", "")

        # Generate signature
        signature_bytes = bytes(credentials, "US-ASCII")
        signature = str(base64.b64encode(signature_bytes))[1:]
        signature = signature.strip("\'")

        # Check if unnecessary
        # Delete credential vars
        del client_id
        del client_secret
        del credentials
        del signature_bytes

        return signature

    def get_auth_headers(self) -> dict:
        ini_section = 'Headers'
        auth_headers = {'Authorization': f"Basic {self.signature}"}
        for attr in self.config[ini_section]:
            auth_headers[attr] = self.config[ini_section][attr]
        return auth_headers

    def get_auth_body(self) -> dict:
        ini_section = 'Body'
        auth_body = {}
        for attr in self.config[ini_section]:
            auth_body[attr] = self.config[ini_section][attr]
        return auth_body

    # Requests an auth token
    def request_auth_token(self) -> str:
        request = requests.Request("POST", url=self.token_url, data=self.token_body, headers=self.token_headers)
        prepped = request.prepare()

        # Create session
        with requests.Session() as session:
            response = session.send(prepped)

        return response.text

    # Requests a refreshed token
    def refresh_auth_token(self):

        return


oclc_session = OCLCSession("config.ini")
