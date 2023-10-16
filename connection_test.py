import requests
from requests.auth import HTTPBasicAuth
from rauth import OAuth2Service
import json
import hmac
import hashlib
import base64
import sys


SECRETS_FILE = ".secrets"

token_url = "https://oauth.oclc.org/token"
token_url_end = "?grant_type=client_credentials&scope=wcapi%20context:285"
auth_url = "https://oauth.oclc.org/auth"
base_url = "https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs-retained-holdings"


file = open(SECRETS_FILE)

cli_id = file.readline()
cli_secret = file.readline()

headers = {
    "name": "OCLC",
    "client_id": cli_id,
    "client_secret": cli_secret,
    "access_token_url": "https://oauth.oclc.org/token",
    "authorize_url": "https://oauth.oclc.org/auth"
}

data = {
    "grant_type": "client_credentials",
    "scope": "wcapi"
}


# Success!
def sixth():
    usr_login = f"{cli_id}:{cli_secret}"
    usr_login = usr_login.replace("\n", "")

    usr_pass = bytes(usr_login, "US-ASCII")
    b64_val = base64.b64encode(usr_pass)
    b64_text = str(b64_val)
    b64_text = b64_text[1:]

    signature = b64_text.strip("\'")

    print(signature)

    headers6 = {
        "Authorization": f"Basic {signature}",
        "Accept": "application/json",
        "context": "285",
        "grant_type": "client_credentials",
        "scope": "wcapi"
    }

    body6 = {
        "grant_type": "client_credentials",
        "scope": "wcapi",
        "context": "285"
    }

    request6 = requests.Request("POST", url=token_url, data=body6, headers=headers6)
    prepped = request6.prepare()

    print(request6.url)
    print(request6.headers)
    print(request6.data)

    print()

    print(prepped.url)
    print(prepped.headers)
    print(prepped.body)

    print()

    with requests.Session() as session:
        response6 = session.send(prepped)

    print(response6.status_code)
    print(response6.text)

    return


def auth_test():
    usr_pass = bytes(f"{cli_id}:{cli_secret}", "US-ASCII")
    b64_val = base64.b64encode(usr_pass).decode("ascii")
    b64_text = str(b64_val)
    b64_text = b64_text[1:]

    signature = b64_text.strip("\'")

    print(signature)
    return


sixth()
