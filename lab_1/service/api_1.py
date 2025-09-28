from .base import BaseApi
from .exceptions import ApiError
import requests


class Api1(BaseApi):
    """ Класс для реализация работы с первым апи	"""
    def __init__(self, api_key: str):
        base_url = "https://brand-recognition.p.rapidapi.com/v2/results"
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "brand-recognition.p.rapidapi.com",
        }
        super().__init__(base_url, headers)

    def recognize_logo(self, image_path: str):
        query_parrams = {"detailed": "True"}

        with open(image_path, "rb") as img_file:
            files = {
                "image": img_file,
            }
            response = requests.post(
                self.base_url,
                headers=self.headers,
                params=query_parrams,
                files=files
            )
            if response.status_code != 200:
                raise ApiError(response.text, response.status_code)

        return self.parse_result(response.json())

    def parse_result(self, response):
        """ Парсинг ответа от первого апи
        :param ответ в формате json/ошибка:

        :rtype: dict
        :returns: информация о задатекеном лого/логотипах
        """
        brands = []
        try:
            results = response.get("results", [])
            entities = results[0].get("entities", [])
            array = entities[0].get("array", [])

            for brand in array:
                name = brand.get("name")
                size_category = brand.get("size_category")
                width = brand.get("width")
                height = brand.get("height")
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
