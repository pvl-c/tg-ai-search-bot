from aiogram import types, Router, F
from voice_utils import transcribe_voice
from search import search_profiles
import logging

router = Router()

@router.message(F.text == "/start")
async def start_handler(message: types.Message):
    await message.answer("Привет! Отправь голосовое или текстовое сообщение с описанием, кого ты ищешь.")

# @router.message(F.voice)
# async def voice_handler(message: types.Message):
#     file = await message.bot.get_file(message.voice.file_id)
#     file_path = file.file_path
#     file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_path}"
#
#     text = transcribe_voice(file_url)
#     if not text:
#         await message.reply("Не удалось расшифровать голос.")
#         return
#
#     await handle_search(message, text)

@router.message(F.voice)
async def voice_handler(message: types.Message):
    try:
        logging.info("Получено голосовое сообщение")
        await message.reply("⏳ Обрабатываю голосовое...")

        file = await message.bot.get_file(message.voice.file_id)
        logging.warning(f"File object: {file}")

        file_path = file.file_path
        file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_path}"
        logging.warning(f"Сформирован file_url: {file_url}")

        text = transcribe_voice(file_url)
        logging.warning(f"Распознанный текст: {text}")

        if not text:
            await message.reply("❌ Не удалось расшифровать голос.")
            logging.warning("Whisper вернул пустой результат.")
            return

        await message.reply(f"🔍 Ищу по запросу: “{text}”")
        await handle_search(message, text)

    except Exception as e:
        logging.exception("Ошибка при обработке голосового сообщения")
        await message.reply("Произошла ошибка при обработке голосового. См. логи.")

@router.message(F.text)
async def text_handler(message: types.Message):
    await handle_search(message, message.text)

async def handle_search(message: types.Message, query: str):
    results = search_profiles(query)
    if not results:
        await message.reply("Никого не нашёл.")
        return

    response = "\n\n".join([f"👤 {r['name']}\n{r['desc']}\n{r['link']}" for r in results])
    await message.reply(response)


def register_handlers(dp):
    dp.include_router(router)
