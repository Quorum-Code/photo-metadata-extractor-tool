import requests


class Query:
    def __init__(self, method, url, headers, data, params):
        self.method = method
        self.url = url
        self.headers = headers
        self.data = data
        self.params = params

        self.response = None

    def send_request(self):
        request = requests.Request(self.method, url=self.url, headers=self.headers, data=self.data, params=self.params)
        prepped = request.prepare()
        with requests.Session() as session:
            self.response = session.send(prepped)
