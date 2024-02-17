import requests
import json
import base64
import configparser
import csv_handler as csvh


class OCLCHandler:
    def __init__(self, configuration: dict, secrets: dict, csv_path: str):
        self.__config = configuration
        self.__secrets = secrets
        self.__csv_path = csv_path
