import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from typing import Dict, Any, List, Optional
import api as hf_api
from service.utils import (
    TG_TOKEN,
    HF_TOKEN,
    MODELS,
    RECOMMENDATION_PROMPT,
    REFINED_RECOMMENDATION_PROMPT,
    QUESTION_PROMPT,
    make_description,
    make_message,
)
from service.user_state import BookFlow
from service.keyboard import choose_model_kb, agree_or_not_kb, like_reco_kb

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
hf_client = hf_api.HuggingFaceAPI(HF_TOKEN)

async def call_api(api_call, *args, error_message: str = "Произошла ошибка"):
    try:
        return await asyncio.to_thread(api_call, *args)
    except hf_api.HFExeption as e:
        return f"{error_message}: {str(e)}"
    except Exception as e:
        return f"{error_message}: Неизвестная ошибка"


@dp.message(Command("start"))
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Привет! Я бот для подбора книги на вечер!")
        await message.answer("Отвечайте на мои вопросы в чате)")
    await message.answer(
        "Выбери модель, которая поможет найти лучшую книгу",
        reply_markup=choose_model_kb(),
    )
    await state.set_state(BookFlow.model)


@dp.callback_query(F.data.startswith("model:"), BookFlow.model)
async def pick_model(callback: F.callback_query, state: FSMContext) -> None:
    model = callback.data[len("model:"):]
    await state.update_data(model=model)
    await callback.message.answer("Выберите жанр:")
    await state.set_state(BookFlow.genre)
    await callback.answer()


@dp.message(BookFlow.genre)
async def handle_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text.strip())
    await message.answer("Возрастное ограничение")
    await state.set_state(BookFlow.age)


@dp.message(BookFlow.age)
async def handle_age(message: Message, state: FSMContext) -> None:
    await state.update_data(age=message.text.strip())
    await message.answer(
        "Есть ли авторы, которых не стоит рекомендовать?",
        reply_markup=agree_or_not_kb(),
    )
    await state.set_state(BookFlow.has_disliked_authors)


@dp.callback_query(F.data == "choice:no", BookFlow.has_disliked_authors)
async def no_disliked_authors(callback: F.callback_query, state: FSMContext) -> None:
    await state.update_data(disliked_authors=None)
    await finish_recs(callback.message, state)
    await callback.answer()


@dp.callback_query(F.data == "choice:yes", BookFlow.has_disliked_authors)
async def has_disliked_authors(callback: F.callback_query, state: FSMContext) -> None:
    await callback.message.answer("Перечислите нелюбимых авторов через запятую")
    await state.set_state(BookFlow.disliked_authors_input)
    await callback.answer()


@dp.message(BookFlow.disliked_authors_input)
async def handle_disliked_authors(message: Message, state: FSMContext) -> None:
    await state.update_data(disliked_authors=message.text.strip())
    await finish_recs(message, state)


async def finish_recs(message: Message, state: FSMContext) -> None:
    data: Dict[str, Any] = await state.get_data()
    model, user_desc = make_description(data)
    messages = make_message(RECOMMENDATION_PROMPT, user_desc)

    await message.answer("Подожите немного, усердно ищу")
    # если напрямую делать запрос через requests (а он синхронный)
    # то бот будет блокаться, будем ждать ответа
    # поэтому явно через asyncio в отдельный поток
    response_text: str = await call_api(
        hf_client.chat_completion, 
        model, 
        messages
    )

    await message.answer(response_text)
    await message.answer("Что скажете?", reply_markup=like_reco_kb())
    await state.update_data(last_recommendation=response_text)
    await state.set_state(BookFlow.feedback)


@dp.callback_query(F.data == "liked:yes", BookFlow.feedback)
async def liked_reco(callback: F.callback_query, state: FSMContext) -> None:
    await callback.message.answer("Ура! Вам нужна еще книга?")
    await callback.message.answer(
        "Для этого укажите модель", reply_markup=choose_model_kb()
    )
    await state.set_state(BookFlow.model)
    await callback.answer()


@dp.callback_query(F.data == "liked:no", BookFlow.feedback)
async def disliked_reco(callback: F.callback_query, state: FSMContext) -> None:
    data: Dict[str, Any] = await state.get_data()
    last_rec: str = data.get("last_recommendation", "неизвестная книга")
    disliked_books: List[str] = data.get("disliked_books", [])
    disliked_books.append(last_rec)
    await state.update_data(disliked_books=disliked_books)

    await callback.message.answer(
        "Ответьте на несколько вопросов,\
                                  чтобы улучшить рекомендации"
    )

    model: str = data.get("model", MODELS[0])
    genre: str = data.get("genre", "не указан")
    age: str = data.get("age", "не указано")
    disliked_authors: Optional[str] = data.get("disliked_authors")

    context_for_questions: str = (
        f"Жанр: {genre}. \
        Возрастное ограничение: {age}."
    )
    if disliked_authors:
        context_for_questions += f"НЕЛЬЗЯ РЕКОМЕНДОВАТЬ АВТОРОВ: {disliked_authors}."
    context_for_questions += f"Последняя рекомендация:\
        <{last_rec}> НЕ ПОНРАВИЛАСЬ"

    messages = make_message(QUESTION_PROMPT, context_for_questions)
    questions_text: str = await call_api(
        hf_client.chat_completion, 
        model, 
        messages
    )
    await callback.message.answer(questions_text)
    await state.set_state(BookFlow.explanation)
    await callback.answer()


@dp.message(BookFlow.explanation)
async def handle_explanation(message: Message, state: FSMContext) -> None:
    explanation_answer: str = message.text.strip()
    data: Dict[str, Any] = await state.get_data()

    model, user_desc = make_description(data, explanation_answer)
    messages = make_message(REFINED_RECOMMENDATION_PROMPT, user_desc)

    await message.answer("Пробую усерднее(")
    response_text: str = await call_api(
        hf_client.chat_completion, 
        model, 
        messages
    )
    await message.answer(response_text)
    await message.answer("Что скажете?", reply_markup=like_reco_kb())
    await state.update_data(last_recommendation=response_text)
    await state.set_state(BookFlow.feedback)


@dp.message(Command("help"))
async def help_cmd(message: Message) -> None:
    await message.answer("/start — начать выбор книги\n" "/help — список команд")


async def main() -> None:
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
