import unittest
import os
from oclc.oclc_api import *


class TestOCLCAPI(unittest.TestCase):
    def setUp(self):
        self.has_secrets = False
        if os.path.exists(".secrets"):
            self.good_session = OCLCSession("config.ini")
            self.has_secrets = True

        self.bad_session = OCLCSession("tests/test_config.ini")

    def tearDown(self):
        pass

    def test_has_secrets(self):
        self.assertEqual(self.has_secrets, True)

    # TODO convert to unittest assert
    def test_is_internet_live(self):
        response_200 = requests.get('https://www.google.com/')
        response_204 = requests.get('https://www.google.com/generate_204')
        response_404 = requests.get('https://www.google.com/404')

        assert response_200.status_code == 200
        assert response_204.status_code == 204
        assert response_404.status_code == 404

    # TODO convert to unittest assert
    def test_is_service_live(self):
        token_response = requests.get('https://oauth.oclc.org/token')
        auth_response = requests.get('https://oauth.oclc.org/auth')

        assert token_response.status_code != 404
        assert auth_response.status_code != 404

    def test_config_valid(self):
        self.assertEqual(self.good_session.token_url, "https://oauth.oclc.org/token")
        self.assertEqual(self.good_session.auth_url, "https://oauth.oclc.org/auth")
        self.assertEqual(self.good_session.metadata_service_url,
                         "https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs")

        assert self.bad_session.token_url == "https://www.google.com/"
        assert self.bad_session.auth_url == "https://www.google.com/generate_204"
        assert self.bad_session.metadata_service_url == "https://www.google.com/404"

    def test_session_initialization(self):
        if self.has_secrets:
            self.assertEqual(self.good_session.hasToken, True)

        self.assertEqual(self.bad_session.hasToken, False)

    def test_credentials_to_signature(self):
        pass

    def test_credentials_valid(self):
        pass


if __name__ == '__main__':
    unittest.main()
