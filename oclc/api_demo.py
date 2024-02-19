# This file demos the functional area API Database Requests
from oclc.oclc_api import OCLCSession


# def simple_demo():
#     """
#     A simple live demo for CS 458 assignment.
#     """
#     # Creates new session with login credentials
#     oclc_session = OCLCSession()
#     print("OCLC Session created...\n")
#
#     # Display token request
#     token_request = oclc_session.printable_token_request()
#     print(f"Token Request...\n"
#           f"---------------------------\n"
#           f"\n{token_request}\n")
#
#     # Print authorization token
#     print(f"Auth Token...\n"
#           f"---------------------------\n"
#           f"{oclc_session.token}\n")
#
#     # Display simple query
#     sudoc = "y4f762el1s2"
#     query_text = oclc_session.printable_query(sudoc)
#     print(f"Simple Query...\n"
#           f"---------------------------\n"
#           f"{query_text}\n")
#
#     # Display results
#     results = oclc_session.query(sudoc)
#     print(results)
#
#     return


# simple_demo()
