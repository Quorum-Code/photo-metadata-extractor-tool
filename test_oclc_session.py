import unittest
# TODO create oclc_api package, then 'import oclc_api'
from oclc_api import *


class TestOCLCAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.good_session = OCLCSession()
        self.bad_session = OCLCSession("tests/oclc_session/test_config.ini")

    def tearDown(self) -> None:
        pass

    # Check no issues with requests
    def test_is_internet_live(self):
        response_200 = requests.get('https://www.google.com/')
        response_204 = requests.get('https://www.google.com/generate_204')
        response_404 = requests.get('https://www.google.com/404')
        self.assertEqual(response_200.status_code, 200)
        self.assertEqual(response_204.status_code, 204)
        self.assertEqual(response_404.status_code, 404)

    # Check that OCLC api is responsive
    def test_is_service_live(self):
        token_response = requests.get('https://oauth.oclc.org/token')
        auth_response = requests.get('https://oauth.oclc.org/auth')
        self.assertNotEqual(token_response.status_code, 404)
        self.assertNotEqual(auth_response.status_code, 404)

    def test_session_initialization(self):
        self.assertEqual(self.good_session.hasToken, True)
        self.assertEqual(self.bad_session.hasToken, False)

        print(self.bad_session.signature)  # Sm9obm55OmFiYzEyMw==

    def test_credentials_to_signature(self):
        pass

    def test_credentials_valid(self):
        pass

    def test_config_valid(self):
        self.assertEqual(self.good_session.token_url, "https://oauth.oclc.org/token")
        self.assertEqual(self.good_session.auth_url, "https://oauth.oclc.org/auth")
        self.assertEqual(self.good_session.metadata_service_url,
                         "https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs")

        self.assertEqual(self.bad_session.token_url, "https://www.google.com/")
        self.assertEqual(self.bad_session.auth_url, "https://www.google.com/generate_204")
        self.assertEqual(self.bad_session.metadata_service_url, "https://www.google.com/404")

    # Initialization
    # No response
    # Signature
    # Credentials
    # Live response tests
    # Mocked response tests


# Runs unit test if this file is directly run
if __name__ == '__main__':
    unittest.main()
