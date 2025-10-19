from dotenv import load_dotenv
import os
from typing import List, Tuple, Dict, Any, Optional

load_dotenv()
TG_TOKEN: str = os.getenv("TG_TOKEN")
HF_TOKEN: str = os.getenv("HF_TOKEN")

MODELS: List[str] = [
    "Qwen/Qwen3-4B-Instruct-2507:nscale",
    "deepseek-ai/DeepSeek-V3.2-Exp:novita",
    "openai/gpt-oss-20b:groq",
]

# Промпты для модели вынесены, чтобы избавиться от повторяющегося кода
RECOMMENDATION_PROMPT: str = (
    "Ты - эксперт в литературе, твоя задача порекомендовать ОДНУ книгу или цикл книг в формате Название: Автор"
    "Дай краткое описание сюжета без спойлеров (2-3 предложения)"
    "НЕЛЬЗЯ РЕКОМЕНДОВАТЬ АВТОРОВ указанных в запросе. Ответ дай на русском языке."
    "НЕ показывай своих рассуждений, только книга, автор и небольшое описание"
)

REFINED_RECOMMENDATION_PROMPT: str = (
    "Ты - эксперт в литературе, Порекомендуй ОДНУ или цикл книг в формате Название: Автор"
    "Дай краткое описание сюжета без спойлеров (2-3 предложения) с учетом уточнений пользователя"
    "Строго избегай книг, авторов и тем, которые пользователь отверг. Ответ дай на русском языке."
    "НЕ показывай своих рассуждений, только книга, автор и небольшое описание"
)

QUESTION_PROMPT: str = (
    "Ты - эксперт в литературе. Пользователю не понравилась твоя рекомендация."
    "Сформулируй 1 или 2 коротких, вежливых уточняющих вопроса на русском языке, чтобы понять"
    " что не понравилось пользователю"
    "Выведи только вопросы, без пояснений."
)


def make_description(
    data: Dict[str, Any], clarification_answer=None
) -> Tuple[str, str]:
    """
    Функция для уточнения системного промпта для модели

    Args:
        data ([type]): [description]
        clarification_answer ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    # Получаем данные из ответов пользователя
    model: str = data.get("model", MODELS[0])
    genre: str = data.get("genre", "не указан")
    age: str = data.get("age", "не указано")
    disliked_authors: Optional[str] = data.get("disliked_authors")
    disliked_books: List[str] = data.get("disliked_books", [])
    # Начинаем формировать информацию для запроса к модели
    description: str = f"Жанр: {genre}. Возрастное ограничение: {age}."
    # Задаем ограничения по авторам и книгам
    # (в случае если были рекомендации, что не понравились)
    if disliked_authors:
        description += f"НЕЛЬЗЯ РЕКОМЕНДОВАТЬ АВТОРОВ {disliked_authors}."
    if disliked_books:
        recent_disliked = " | ".join(disliked_books[-3:])
        description += f" Ранее НЕ ПОНРАВИЛИСЬ рекомендации: {recent_disliked}."
    # Добавляем уточнения от пользователя, если были заданы уточняющие вопросы от модели
    if clarification_answer:
        description += f"\nУточнение от пользователя: {clarification_answer}"

    return model, description


def make_message(system_prompt: str, user_content: str) -> List[Dict[str, str]]:
    # Чтобы не засорять код однотипным кодом, вынесла в функцию
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
