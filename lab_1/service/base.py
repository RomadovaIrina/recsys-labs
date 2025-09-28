import requests


class BaseApi:
    """ Базовый класс для реализации запросов к АПИ	"""
    def __init__(self, base_url: str, headers: dict):
        self.base_url = base_url
        self.headers = headers

    def post(self, endpoint: str, payload: dict):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.post(url, data=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {f'errorr: {e}'}
