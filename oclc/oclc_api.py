import requests
import json
import base64
import configparser


class OCLCSession:
    """
    Attributes:
        token_url : str
            The url for token requests.
        auth_url : str
            The url for authentication requests.
        metadata_service_url : str
            The url for queries.

        signature : str
            The encoded credentials.
        token_headers : dict
            Headers for an authentication request.
        token_body : dict
            Body for an authentication request.
        token : str
            Acquired authentication token.

        query_headers : dict
            Headers for a query.
        query_body : dict
            Body for a query.
    """

    def __init__(self, config_file="config.ini", secrets_file=".secrets"):
        """
        Encapsulates all the functions and data required to connect to the OCLC API,
        query the API, and process the returned data.

        :param config_file: The name of the config file in the program folder.

        :param secrets_file: Optional path to secrets file containing credentials.
        """

        # Files
        self.config_file = config_file
        self.secrets_file = secrets_file

        # Config settings
        self.config = configparser.ConfigParser()
        self.config.sections()
        self.config.read(self.config_file)

        # URLs
        self.token_url = self.config['URLS']['token_url']
        self.auth_url = self.config['URLS']['auth_url']
        self.metadata_service_url = self.config['URLS']['metadata_service_url']

        # Auth-token setup
        self.signature = self.get_signature()
        self.token_headers = self.get_auth_headers()
        self.token_body = self.get_auth_body()

        # Request Auth token
        self.auth_response = ""
        self.hasToken = False
        self.token = None
        self.request_auth_token()

        # Query setup
        self.query_headers = self.get_query_headers()
        self.query_body = self.get_query_body()

    def printable_token_request(self) -> str:
        printable = ""

        printable += f"URL : {self.token_url}\n"
        printable += f"Headers : {self.token_headers}\n"
        printable += f"Body : {self.token_body}\n"

        return printable

    def printable_query(self, sudoc: str) -> str:
        printable = ""
        self.query_body['q'] = f"gn:{sudoc}"

        printable += f"URL : {self.metadata_service_url}\n"
        printable += f"Headers : {self.query_headers}\n"
        printable += f"Body : {self.query_body}\n"

        return printable

    def get_signature(self) -> str:
        """
        Encodes the client credentials needed to get an authentication token.

        :return: The signature to attach to an authentication request.
        """

        # Get credentials
        # secrets_file = self.config['Directories']['secrets']
        secrets = configparser.ConfigParser()
        secrets.sections()
        secrets.read(self.secrets_file)

        client_id = secrets['SECRETS']['client_id']
        client_secret = secrets['SECRETS']['client_secret']

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

        # return signature
        return signature

    def get_auth_headers(self) -> dict:
        """
        Formats the authentication headers corresponding to the config file of the session.

        :return: The dict of formatted headers for an authentication request.
        """

        ini_section = 'Headers'
        auth_headers = {'Authorization': f"Basic {self.signature}"}
        for attr in self.config[ini_section]:
            auth_headers[attr] = self.config[ini_section][attr]
        return auth_headers

    def get_auth_body(self) -> dict:
        """
        Formats the authentication body corresponding to the config file of the session.

        :return: The dict of formatted body for an authentication request.
        """

        ini_section = 'Body'
        auth_body = {}
        for attr in self.config[ini_section]:
            auth_body[attr] = self.config[ini_section][attr]
        return auth_body

    # Requests an auth token
    def request_auth_token(self):
        """
        Sends a query to the OCLC API for an authentication token.

        :return: The acquired authentication token as a string.
        """

        request = requests.Request("POST", url=self.token_url, data=self.token_body, headers=self.token_headers)
        prepped = request.prepare()

        # Create session
        with requests.Session() as session:
            response = session.send(prepped)

        if response:
            self.auth_response = response.text
            response_json = json.loads(response.text)

            if 'access_token' in response_json:
                token = response_json['access_token']
                self.hasToken = True
                self.token = token
            else:
                self.hasToken = False
                self.token = None

    def get_query_headers(self) -> dict:
        """
        Formats the query headers for a bibliographic search query.

        :return: The dict containing headers for bibliographic search.
        """

        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        return headers

    def get_query_body(self) -> dict:
        """
        Formats the query body for a bibliographic search query.

        :return: The dict containing parameters for bibliographic search query.
        """

        registry_ids = self.config['Institution-IDS']['registry_ids']

        body = {
            'q': '',
            'heldByInstitutionID': f'{registry_ids}',
            'itemType': '',
            'itemSubType': '',
            'retentionCommitments': 'false',
            'facets': 'content',
            'groupRelatedEditions': 'false',
            'groupVariantRecords': 'false',
            'orderBy': 'bestMatch',
            'offset': '1',
            'limit': '10'
        }

        return body

    def query(self, sudoc: str) -> str:
        """
        Sends a query to the OCLC API to search for a document from the given SuDoc.

        :param sudoc: SuDoc number of desired document.
        :return: The response from the query formatted as JSON text.
        """

        self.query_body['q'] = f"gn:{sudoc}"

        query_request = requests.Request("GET",
                                         url=self.metadata_service_url,
                                         headers=self.query_headers,
                                         params=self.query_body)
        query_prepped = query_request.prepare()

        with requests.Session() as session:
            response = session.send(query_prepped)

        return response.text


if __name__ == "__main__":
    oclcsession = OCLCSession("config.ini")
    print(f"Qh: {oclcsession.query_headers}")
    print(f"Qb: {oclcsession.query_body}")
    print(f"Ah: {oclcsession.get_auth_headers()}")
    print(f"Ab: {oclcsession.get_auth_body()}")
