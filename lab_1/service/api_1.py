from .exceptions import ApiError
import requests
from typing import List, Dict


class Api1:
    """Класс для реализации работы с первым API"""

    def __init__(self, api_key: str):
        self.base_url: str = (
            "https://brand-recognition.p.rapidapi.com/v2/results"  # noqa: E501
        )
        self.headers: Dict[str, str] = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "brand-recognition.p.rapidapi.com",
        }

    def recognize_logo(self, image: bytes) -> List[Dict[str, str]]:
        query_parrams: Dict[str, str] = {"detailed": "True"}

        files: Dict[str, bytes] = {"image": image}

        response: requests.Response = requests.post(
            self.base_url, headers=self.headers, params=query_parrams, files=files
        )
        if response.status_code != 200:
            raise ApiError(response.text, response.status_code)

        return self.parse_result(response.json())

    def parse_result(self, response: Dict) -> List[Dict[str, str]]:
        """Парсинг ответа от первого API
        :param ответ в формате json/ошибка:

        :rtype: dict
        :returns: информация о задатекеном лого/логотипах
        """
        brands: List[Dict[str, str]] = []
        try:
            results = response.get("results", [])
            entities = results[0].get("entities", [])
            array = entities[0].get("array", [])

            for brand in array:
                name: str = brand.get("name")
                size_category: str = brand.get("size_category")
                width: str = brand.get("width")
                height: str = brand.get("height")
                brands.append(
                    {
                        "Марка": name,
                        "Размер": size_category,
                        "Ширина": width,
                        "Высота": height,
                    }
                )
        except Exception as e:
            return {"error": f"error_parse: {str(e)}"}

        return brands
