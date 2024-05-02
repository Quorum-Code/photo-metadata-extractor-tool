import typing

import requests
import json
import base64
import configparser
import string

import json_parser
from file_handler import FileHandler
from csv_handlers.csv_handler import CSVDocument, SuDocRecord
from csv_handlers.csv_reader import *
from csv_handlers.csv_writer import *


class OCLCSession:
    def __init__(self, file_handler: FileHandler, config_file="config.ini", secrets_file=".secrets"):
        self.__file_handler = file_handler

        if type(self.__file_handler) is not FileHandler:
            print("ERROR: Passed invalid FileHandler...")
            return

        self.__token_url = self.__file_handler.get_token_url()
        self.__token_headers = self.__file_handler.get_token_headers()
        self.__token_body = self.__file_handler.get_token_body()
        self.__token: str = ""
        self.__signature = self.__get_signature()
        self.__query_url = self.__file_handler.get_query_url()
        self.__query_headers = self.__file_handler.get_query_headers()
        self.__query_parameters = self.__file_handler.get_query_parameters()

        # Config settings
        # self.config = configparser.ConfigParser()
        # self.config.sections()
        # self.config.read(self.config_file)
        #
        # # URLs
        # self.token_url = self.config['URLS']['token_url']
        # self.auth_url = self.config['URLS']['auth_url']
        # self.metadata_service_url = self.config['URLS']['metadata_service_url']
        #
        # # Auth-token setup
        # self.signature = self.get_signature()
        # self.token_headers = self.get_auth_headers()
        # self.token_body = self.get_auth_body()
        #
        # # Request Auth token
        # self.auth_response = ""
        # self.hasToken = False
        # self.token = None
        # self.request_auth_token()
        #
        # # Query setup
        # self.query_headers = self.get_query_headers()
        # self.query_body = self.get_query_body()

    def ready_session(self) -> bool:
        """
        Readies session by requesting an access token.
        """
        # inject signature into token_body
        self.__token_headers["Authorization"] = f"Basic {self.__signature}"

        # create token request
        token_request = requests.Request("POST", url=self.__token_url,
                                         data=self.__token_body, headers=self.__token_headers)
        token_request_prepped = token_request.prepare()

        # Send request
        with requests.Session() as session:
            token_response = session.send(token_request_prepped)

        # Process response
        if token_response:
            token_response_json = json.loads(token_response.text)
            if "access_token" in token_response_json:
                token = token_response_json["access_token"]
                self.__token = token
                self.__query_headers["Authorization"] = f"Bearer {self.__token}"
                return True
            else:
                print("no access token in response")
                return False
        else:
            print("no response")
            return False

    def query_csv_sudoc(self, csv_file_path: str, update_progress_percent: typing.Callable[[float], None]) -> bool:
        # Create csv object
        # csv_doc = CSVDocument(self.__file_handler, file_path=csv_file_path, read_only=True)
        csv_reader = CSVReader(csv_file_path)

        # get list of sudocs
        sudocs = csv_reader.get_query_terms()
        print(f"Terms: {sudocs}")
        for sudoc in sudocs:
            print("a_sudoc: " + sudoc)

        # filter sudocs
        filtered_sudocs = self.__filter_sudocs(sudocs)

        csv_writer = CSVWriter(self.__file_handler.query_result_folder_path())
        jp = json_parser.JSONParser(json_parser.DEFAULT_KEY_MAP)

        # iterate through list of sudocs
        result: list[dict[str]] = []
        for i in range(len(filtered_sudocs)):
            text = self.__query_term(filtered_sudocs[i])
            jd = json.loads(text)

            row: dict[str, str] = {}
            if "bibRecords" in jd and len(jd["bibRecords"]) > 0:
                row = jp.get_values(jd["bibRecords"][0])

            print(f"ROW: {row}")
            result.append(row)
        # print(f"jp_cols: {jp.get_cols()}")
        # csv_writer.write_data(jp.get_cols(), result)
        # csv_writer.

        self.__query_parameters['q'] = ""

        return True

    def __add_sudoc_record(self, doc: CSVDocument, raw_sudoc: str, json_text: str):
        if json_text == "":
            return

        j = json.loads(json_text)

        print("made it here")

        if "numberOfRecords" not in j:
            doc.add_row(SuDocRecord(raw_sudoc, "no response", "", "", "", "", "").get_dict())
            return

        if j["numberOfRecords"] <= 0:
            doc.add_row(SuDocRecord(raw_sudoc, "no records found", "", "", "", "", "").get_dict())
            return

        n_records = j["numberOfRecords"]
        if j["numberOfRecords"] > 1:
            status = "multiple records found"
        elif j["numberOfRecords"] == 1:
            status = "single record found"
        else:
            status = "no records found"

        for i in range(n_records):
            doc.add_row(self.__bib_record_to_sudoc_record(raw_sudoc, status, j["bibRecords"][i]).get_dict())

        print("n_records type: ", type(n_records))
        print(n_records)

    def __bib_record_to_sudoc_record(self, raw_sudoc: str, status: str, bib: dict) -> SuDocRecord:
        filtered_sudoc = ""

        gov_num = ""
        title = ""
        author = ""
        pub_date = ""

        if "classification" in bib and "govDoc" in bib["classification"]:
            gov_num = bib["classification"]["govDoc"][0]

        if "date" in bib and "publicationDate" in bib["date"]:
            pub_date = bib["date"]["publicationDate"]

        if "title" in bib and "mainTitles" in bib["title"]:
            title = bib["title"]["mainTitles"][0]["text"]

        sr = SuDocRecord(raw_sudoc, status, gov_num, filtered_sudoc, title, author, pub_date)
        return sr

    def __query_term(self, sudoc: str) -> str:
        print("Querying: " + sudoc)

        # query filtered sudoc
        qt = self.__file_handler.get_query_type()
        self.__query_parameters['q'] = f"{qt}:{sudoc}"
        query_request = requests.Request(method="GET",
                                         url=self.__query_url,
                                         headers=self.__query_headers,
                                         params=self.__query_parameters)
        query_prepped = query_request.prepare()

        with requests.Session() as session:
            response = session.send(query_prepped)

        return response.text

    def __query_sudoc(self, sudoc: str) -> str:
        print("Querying: " + sudoc)

        # query filtered sudoc
        self.__query_parameters['q'] = f"gn:{sudoc}"
        query_request = requests.Request(method="GET",
                                         url=self.__query_url,
                                         headers=self.__query_headers,
                                         params=self.__query_parameters)
        query_prepped = query_request.prepare()

        with requests.Session() as session:
            response = session.send(query_prepped)

        return response.text

    def __filter_sudocs(self, sudocs: list[str]) -> list[str]:
        filtered_sudocs = []

        whitespace_translator = str.maketrans("", "", string.whitespace)
        punctuation_translator = str.maketrans("", "", string.punctuation)

        for i in range(len(sudocs)):
            filtered_sudocs.append(sudocs[i].translate(whitespace_translator).translate(punctuation_translator))

        return filtered_sudocs

    def __get_signature(self) -> str:
        client_id, client_secret = self.__file_handler.get_secrets()

        # Unsigned credentials
        credentials = f"{client_id}:{client_secret}"
        credentials = credentials.replace("\n", "")

        # Generate signature
        signature_bytes = bytes(credentials, "US-ASCII")
        signature = str(base64.b64encode(signature_bytes))[1:]
        signature = signature.strip("\'")
        return signature

    # def printable_token_request(self) -> str:
    #     printable = ""
    #
    #     printable += f"URL : {self.token_url}\n"
    #     printable += f"Headers : {self.token_headers}\n"
    #     printable += f"Body : {self.token_body}\n"
    #
    #     return printable
    #
    # def printable_query(self, sudoc: str) -> str:
    #     printable = ""
    #     self.query_body['q'] = f"gn:{sudoc}"
    #
    #     printable += f"URL : {self.metadata_service_url}\n"
    #     printable += f"Headers : {self.query_headers}\n"
    #     printable += f"Body : {self.query_body}\n"
    #
    #     return printable
    #
    # def get_signature(self) -> str:
    #     """
    #     Encodes the client credentials needed to get an authentication token.
    #
    #     :return: The signature to attach to an authentication request.
    #     """
    #
    #     # Get credentials
    #     # secrets_file = self.config['Directories']['secrets']
    #     secrets = configparser.ConfigParser()
    #     secrets.sections()
    #     secrets.read(self.secrets_file)
    #
    #     client_id = secrets['SECRETS']['client_id']
    #     client_secret = secrets['SECRETS']['client_secret']
    #
    #     # Unsigned credentials
    #     credentials = f"{client_id}:{client_secret}"
    #     credentials = credentials.replace("\n", "")
    #
    #     # Generate signature
    #     signature_bytes = bytes(credentials, "US-ASCII")
    #     signature = str(base64.b64encode(signature_bytes))[1:]
    #     signature = signature.strip("\'")
    #
    #     # Check if unnecessary
    #     # Delete credential vars
    #     del client_id
    #     del client_secret
    #     del credentials
    #     del signature_bytes
    #
    #     # return signature

    # def get_auth_headers(self) -> dict:
    #     """
    #     Formats the authentication headers corresponding to the config file of the session.
    #
    #     :return: The dict of formatted headers for an authentication request.
    #     """
    #
    #     ini_section = 'Headers'
    #     auth_headers = {'Authorization': f"Basic {self.signature}"}
    #     for attr in self.config[ini_section]:
    #         auth_headers[attr] = self.config[ini_section][attr]
    #     return auth_headers
    #
    # def get_auth_body(self) -> dict:
    #     """
    #     Formats the authentication body corresponding to the config file of the session.
    #
    #     :return: The dict of formatted body for an authentication request.
    #     """
    #
    #     ini_section = 'Body'
    #     auth_body = {}
    #     for attr in self.config[ini_section]:
    #         auth_body[attr] = self.config[ini_section][attr]
    #     return auth_body

    # Requests an auth token
    # def request_auth_token(self):
    #     """
    #     Sends a query to the OCLC API for an authentication token.
    #
    #     :return: The acquired authentication token as a string.
    #     """
    #
    #     request = requests.Request("POST", url=self.token_url, data=self.token_body, headers=self.token_headers)
    #     prepped = request.prepare()
    #
    #     # Create session
    #     with requests.Session() as session:
    #         response = session.send(prepped)
    #
    #     if response:
    #         self.auth_response = response.text
    #         response_json = json.loads(response.text)
    #
    #         if 'access_token' in response_json:
    #             token = response_json['access_token']
    #             self.hasToken = True
    #             self.token = token
    #         else:
    #             self.hasToken = False
    #             self.token = None
    #
    # def get_query_headers(self) -> dict:
    #     """
    #     Formats the query headers for a bibliographic search query.
    #
    #     :return: The dict containing headers for bibliographic search.
    #     """
    #
    #     headers = {
    #         'accept': 'application/json',
    #         'Authorization': f'Bearer {self.token}'
    #     }
    #     return headers
    #
    # def get_query_body(self) -> dict:
    #     """
    #     Formats the query body for a bibliographic search query.
    #
    #     :return: The dict containing parameters for bibliographic search query.
    #     """
    #
    #     registry_ids = self.config['Institution-IDS']['registry_ids']
    #
    #     body = {
    #         'q': '',
    #         'heldByInstitutionID': f'{registry_ids}',
    #         'itemType': '',
    #         'itemSubType': '',
    #         'retentionCommitments': 'false',
    #         'facets': 'content',
    #         'groupRelatedEditions': 'false',
    #         'groupVariantRecords': 'false',
    #         'orderBy': 'bestMatch',
    #         'offset': '1',
    #         'limit': '10'
    #     }
    #
    #     return body

    # def query(self, sudoc: str) -> str:
    #     """
    #     Sends a query to the OCLC API to search for a document from the given SuDoc.
    #
    #     :param sudoc: SuDoc number of desired document.
    #     :return: The response from the query formatted as JSON text.
    #     """
    #
    #     self.query_body['q'] = f"gn:{sudoc}"
    #
    #     query_request = requests.Request("GET",
    #                                      url=self.metadata_service_url,
    #                                      headers=self.query_headers,
    #                                      params=self.query_body)
    #     query_prepped = query_request.prepare()
    #
    #     with requests.Session() as session:
    #         response = session.send(query_prepped)
    #
    #     return response.text


# if __name__ == "__main__":
#     oclcsession = OCLCSession("config.ini")
#     print(f"Qh: {oclcsession.query_headers}")
#     print(f"Qb: {oclcsession.query_body}")
#     print(f"Ah: {oclcsession.get_auth_headers()}")
#     print(f"Ab: {oclcsession.get_auth_body()}")
