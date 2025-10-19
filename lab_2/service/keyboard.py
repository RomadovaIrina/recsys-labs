from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from service.utils import MODELS
from typing import List


def choose_model_kb() -> InlineKeyboardMarkup:
    """
    Функция для отображения моделей в чате как кнопку
    """
    buttons: List[List[InlineKeyboardMarkup]] = []
    for model in MODELS:
        display_name: str = model.split("/")[-1].split(":")[0]
        buttons.append(
            [InlineKeyboardButton(text=display_name, callback_data=f"model:{model}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def agree_or_not_kb() -> InlineKeyboardMarkup:
    """
    Установка статуса для некотрых вопросов
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data="choice:yes"),
                InlineKeyboardButton(text="Нет", callback_data="choice:no"),
            ]
        ]
    )


def like_reco_kb() -> InlineKeyboardMarkup:
    """
    Кнопка для оценки рекомендаций
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Понравилось", callback_data="liked:yes")],
            [InlineKeyboardButton(text="Не понравилось", callback_data="liked:no")],
        ]
    )
