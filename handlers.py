from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from query_refiner import refine_query
from search import search_profiles
from voice_utils import transcribe_voice
from aiogram.filters import StateFilter

router = Router()

class SearchFSM(StatesGroup):
    awaiting_confirmation = State()

@router.message(F.text == "/start")
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer("👋 Привет! Отправь текст или голосовое сообщение с тем, кого ты ищешь (например: «нужен диджей на рейв в Казани»)")

@router.message(StateFilter(None), F.text)
async def text_handler(message: types.Message, state: FSMContext):
    raw_text = message.text
    await message.answer("🤖 Обрабатываю запрос...")

    refined = refine_query(raw_text)
    if not refined:
        await message.answer("❌ Не смог понять запрос. Попробуй переформулировать.")
        return

    await state.update_data(refined=refined)

    preview = "\n".join([
        f"🔹 Роль: {refined.get('role') or '—'}",
        f"🔹 Стиль: {refined.get('style') or '—'}",
        f"🔹 Локация: {refined.get('location') or '—'}",
        f"🔹 Событие: {refined.get('event') or '—'}",
        f"🔹 Время: {refined.get('preferred_time') or '—'}",
        f"🔹 Дополнительно: {refined.get('other') or '—'}"
    ])

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Да, всё верно"), KeyboardButton(text="❌ Изменить")]
        ],
        resize_keyboard=True
    )

    await message.answer(f"Вы имели в виду:\n\n{preview}", reply_markup=kb)
    await state.set_state(SearchFSM.awaiting_confirmation)

@router.message(F.voice)
async def voice_handler(message: types.Message, state: FSMContext):
    await message.answer("🔊 Расшифровываю голосовое...")

    file = await message.bot.get_file(message.voice.file_id)
    file_path = file.file_path
    file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_path}"

    text = transcribe_voice(file_url)
    if not text:
        await message.answer("❌ Не удалось распознать голос.")
        return

    await message.answer(f"📝 Текст из голосового:\n\n“{text}”\n\n⏳ Обрабатываю запрос...")

    refined = refine_query(text)
    if not refined:
        await message.answer("❌ Не смог понять запрос. Попробуй сказать по-другому.")
        return

    await state.update_data(refined=refined)

    preview = "\n".join([
        f"🔹 Роль: {refined.get('role') or '—'}",
        f"🔹 Стиль: {refined.get('style') or '—'}",
        f"🔹 Локация: {refined.get('location') or '—'}",
        f"🔹 Событие: {refined.get('event') or '—'}",
        f"🔹 Время: {refined.get('preferred_time') or '—'}",
        f"🔹 Дополнительно: {refined.get('other') or '—'}"
    ])

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Да, всё верно"), KeyboardButton(text="❌ Изменить")]
        ],
        resize_keyboard=True
    )

    await message.answer(f"Вы имели в виду:\n\n{preview}", reply_markup=kb)
    await state.set_state(SearchFSM.awaiting_confirmation)

@router.message(SearchFSM.awaiting_confirmation, F.text.in_(["✅ Да, всё верно", "❌ Изменить"]))
async def confirm_handler(message: types.Message, state: FSMContext):
    choice = message.text

    if choice == "❌ Изменить":
        await message.answer("✏️ Ок, отправь новый запрос.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return

    data = await state.get_data()
    refined = data.get("refined")

    if not refined:
        await message.answer("⚠️ Не могу найти запрос. Начни сначала.")
        await state.clear()
        return

    final_query = " ".join(filter(None, [
        refined.get("role", ""),
        "в стиле", refined.get("style", ""),
        "в", refined.get("location", ""),
        "на", refined.get("event", ""),
        refined.get("preferred_time", ""),
        refined.get("other", "")
    ]))

    await message.answer(f"🔍 Ищу: {final_query}", reply_markup=ReplyKeyboardRemove())

    results = search_profiles(final_query)

    if not results:
        await message.answer("Никого не нашёл 😕")
    else:
        response = "\n\n".join([
            f"👤 {r.properties['name']} (score: {r.metadata.score:.2f})\n{r.properties['desc']}\n{r.properties['link']}"
            for r in results
        ])
        await message.answer(response)

    await state.clear()


def register_handlers(dp):
    dp.include_router(router)
