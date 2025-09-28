import requests
from .exceptions import ApiError
from PIL import Image, ImageDraw
from io import BytesIO
from typing import List, Dict, Tuple, Optional


class Api2:
    """
    Класс для работы со вторым API
    """

    def __init__(self, api_key: str):
        self.base_url: str = (
            "https://brand-detection-api1.p.rapidapi.com/api/v1/vision/brand-detection"  # noqa: E501
        )
        self.headers: Dict[str, str] = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "brand-detection-api1.p.rapidapi.com",
        }

    def detect_logo(
        self, image: BytesIO, confidence: float = 0.5
    ) -> Tuple[List[Dict[str, str]], Optional[BytesIO]]:
        """Функция для детекции логотипа и рисования ббоксов
        :param image: Изображение для детекции
        :param confidence: Уровень уверенности для обнаружения логотипов
        :returns: Список с данными о логотипах и изображение с ббоксами/ошибка
        Тк при ошибке картинки нет, то использовала Optional,
        чтобы захватить тип bytesio или none
        """
        query_params: Dict[str, str] = {"confidence": str(confidence)}
        files: Dict[str, BytesIO] = {"file": image}
        response: requests.Response = requests.post(
            self.base_url, headers=self.headers, params=query_params, files=files
        )
        if response.status_code != 200:
            raise ApiError(response.text, response.status_code)
        return self.parse_result(response.json(), image)

    def parse_result(
        self, response: Dict, image: BytesIO
    ) -> Tuple[List[Dict[str, str]], Optional[BytesIO]]:
        """парсит ответ второго API

        :param response: Ответ API, содержащий данные о брендах
        :type response: dict

        :param image: Изображение для рисования bbox-ов
        :type image: BytesIO

        :raises: Возвращает ошибку, если не удается извлечь данные о бренде
        :rtype: list
        :returns: Список словарей с данными о брендах/ошибка
        """
        data = response.get("data", {})
        results = data.get("results", {})
        detected_brands = results.get("detected_brands", [])

        detected_brands: List[Dict[str, str]] = detected_brands

        if not detected_brands:
            return {"error": "Не удалось обнаружить бренды"}, None

        img: Image.Image = Image.open(image)
        draw: ImageDraw.Draw = ImageDraw.Draw(img)

        parsed_brands: List[Dict[str, str]] = []
        for brand in detected_brands:
            name: str = brand.get("brand_name")
            confidence: float = brand.get("confidence")
            bbox: List[int] = brand.get("bbox")  # [left - top, right - bottom]
            top_left: Dict[str, int] = {"x": bbox[0], "y": bbox[1]}
            bottom_right: Dict[str, int] = {"x": bbox[2], "y": bbox[3]}
            if bbox:
                draw.rectangle(bbox, outline="red", width=3)
            parsed_brands.append(
                {
                    "Бренд": name,
                    "Confidence": confidence,
                    "bbox": {"top_left": top_left, "bottom_right": bottom_right},
                }
            )

        img_byte_array: BytesIO = BytesIO()
        img.save(img_byte_array, format="PNG")
        img_byte_array.seek(0)
        img.save("result_image_with_bboxes.png")

        return parsed_brands, img_byte_array
