import requests
from .HF_exception import HF_exception


class HuggingFaceAPI:
    """
    Клиент для взаимодействия с HF через Inference Providers
    """

    API_URL = "https://router.huggingface.co/v1/chat/completions"

    def __init__(self, hf_token: str):
        self.headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json",
        }

    def chat_completion(self, model: str, messages: list) -> str:
        """
        Функция для обращения к модели

        Args:
            model: Модель
            messages: Список сообщений в формате:
                {"role": "system/user",
                "content": "текст"}

        Returns:
            str: Ответ от модели
        """
        try:
            payload = {"model": model, "messages": messages}
            response: requests.Response = requests.post(
                self.API_URL, headers=self.headers, json=payload, timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            raise HF_exception(f"Ошибка: {str(e)}")
