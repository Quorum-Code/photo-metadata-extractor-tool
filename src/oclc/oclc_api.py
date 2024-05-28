import typing
import requests
import json
import base64
import configparser
import string
import datetime as dt

import src.local_data.json_parser
from src.local_data.file_handler import FileHandler
from src.csv_handlers.csv_handler import CSVDocument, SuDocRecord
from src.csv_handlers.csv_reader import *
from src.csv_handlers.csv_writer import *


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

    def ready_session(self) -> bool:
        """
        Readies session by requesting an access token.
        """
        if self.try_cached_token():
            return True

        # inject signature into token_body
        self.__token_headers["Authorization"] = f"Basic {self.__signature}"
        print(self.__token_headers["Authorization"])

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

                self.__file_handler.set_cached_token(token_response_json["access_token"])
                self.__file_handler.set_cached_token_time(token_response_json["expires_at"])
                return True
            else:
                print("no access token in response")
                return False
        else:
            print("no response")
            return False

    def try_cached_token(self) -> bool:
        tkn = self.__file_handler.get_cached_token()
        if tkn == "":
            # No token stored
            return False

        tkn_time = self.__file_handler.get_cached_token_time().replace("Z", "")
        tkn_date = dt.datetime.strptime(tkn_time, "%Y-%m-%d %H:%M:%S") - dt.timedelta(minutes=1)
        now = dt.datetime.utcnow()

        if tkn_date > now:
            # Valid token
            self.__token = tkn
            self.__query_headers["Authorization"] = f"Bearer {self.__token}"
            return True
        # Invalid token
        return False

    def query_csv_sudoc(self, csv_file_path: str, update_progress_percent: typing.Callable[[float], None]) -> str:
        # Create csv object
        csv_reader = CSVReader(csv_file_path)

        # get list of sudocs
        term_name = self.__file_handler.get_query_term_name()
        query_terms = csv_reader.get_query_term(term_name)

        query_profile = self.__file_handler.get_query_profile()
        jp = src.local_data.json_parser.JSONParser(query_profile["key_map"])

        # filter sudocs
        # TODO: make optional within config
        trim_terms = query_profile["trim_terms"]
        filtered_terms = self.__filter_sudocs(query_terms, trim_terms)

        csv_writer = CSVWriter(self.__file_handler.query_result_folder_path())

        # iterate through list of sudocs
        result: list[dict[str, str]] = []
        for i in range(len(filtered_terms)):
            text = self.__query_term(filtered_terms[i])
            jd = json.loads(text)

            row: dict[str, str] = {}
            if "bibRecords" in jd and len(jd["bibRecords"]) > 0:
                row = jp.get_values(jd["bibRecords"][0])
                l = len(jd["bibRecords"])
                if l == 1:
                    row["Query Status"] = "Single record found"
                else:
                    row["Query Status"] = f"Multiple record found: {l} records"

            else:
                row["Query Status"] = "No record found"
            row["Query Term"] = query_terms[i]
            row["Filtered Term"] = filtered_terms[i]

            print(f"ROW: {row}")
            result.append(row)
        col_names = ["Query Term", "Filtered Term", "Query Status"] + jp.get_cols()

        csv_writer.write_data(col_names, result)

        self.__query_parameters['q'] = ""

        return csv_writer.get_abs_path()

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

    def __filter_sudocs(self, sudocs: list[str], trim_terms) -> list[str]:
        filtered_terms = []
        whitespace_translator = str.maketrans("", "", string.whitespace)
        punctuation_translator = str.maketrans("", "", string.punctuation)

        for i in range(len(sudocs)):
            filtered_term = sudocs[i]
            upped = sudocs[i].upper()
            for j in range(len(trim_terms)):
                index = upped.find(trim_terms[j])
                if index != -1:
                    filtered_term = filtered_term[index+len(trim_terms[j]):]
                    break

            filtered_term = filtered_term.translate(whitespace_translator)
            filtered_term = filtered_term.translate(punctuation_translator)

            filtered_terms.append(filtered_term)

        return filtered_terms

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
