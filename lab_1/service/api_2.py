import requests
from .base import BaseApi
from .exceptions import ApiError
from PIL import Image, ImageDraw


class Api2(BaseApi):
    """
    Класс для работы со втроым апи
    """
    def __init__(self, api_key: str):
        base_url = ("https://brand-detection-api1.p.rapidapi.com/api/v1/vision/brand-detection")  # noqa: E501
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "brand-detection-api1.p.rapidapi.com",
        }
        super().__init__(base_url, headers)

    def detect_logo(self, image_path: str, confidence: float = 0.5):
        query_params = {"confidence": str(confidence)}

        with open(image_path, "rb") as img_file:
            files = {
                "file": img_file,
            }
            response = requests.post(
                self.base_url,
                headers=self.headers,
                params=query_params,
                files=files
            )
            if response.status_code != 200:
                raise ApiError(response.text, response.status_code)
        return self.parse_result(response.json(), image_path)

    def parse_result(self, response, image_path):
        """ парсит ответ второго апи

        :param response: Ответ API, содержащий данные о брендах
        :type response: dict

        :param image_path: Изображение для рисования bbox-ов
        :type image_path: str

        :raises: Возвращает ошибку, если не удается извлечь данные о бренде
        :rtype: list
        :returns: Список словарей с данными о брендах/ошибка
        """
        detected_brands = (
            response.get("data", {})
            .get("results", {})
            .get("detected_brands", [])
        )

        if not detected_brands:
            return {"error": "Не удалось обнаружить бренды в изображении."}

        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        parsed_brands = []
        for brand in detected_brands:
            name = brand.get("brand_name")
            confidence = brand.get("confidence")
            bbox = brand.get("bbox")  # [left - top, right - bottom]
            top_left = {"x": bbox[0], "y": bbox[1]}
            bottom_right = {"x": bbox[2], "y": bbox[3]}
            if bbox:
                draw.rectangle(bbox, outline="red", width=3)
            parsed_brands.append(
                {
                    "Бренд": name,
                    "Confidence": {confidence},
                    "bbox": {"top_left": top_left,
                             "bottom_right": bottom_right},
                }
            )

        img.save("result_image_with_bboxes.png")
        return parsed_brands
