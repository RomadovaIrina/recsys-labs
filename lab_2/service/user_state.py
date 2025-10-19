from aiogram.fsm.state import State, StatesGroup


class BookFlow(StatesGroup):
    """
    Класс для состояний,
    которые проходит пользователь для получения рекомендаций
    """

    model = State()
    genre = State()
    age = State()
    # Отвечает за наличие нелюбимых авторов
    # на первой итерации рекомендаций
    has_disliked_authors = State()
    # Для хранения этих нелюбимых авторов
    disliked_authors_input = State()
    feedback = State()
    explanation = State()
