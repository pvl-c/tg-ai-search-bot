import logging
import requests
import openai
import tempfile
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def transcribe_voice(file_url: str) -> str:
    logging.info(f"🔗 Загружаю аудио с URL: {file_url}")

    try:
        response = requests.get(file_url)
        response.raise_for_status()
        logging.info(f"✅ Аудио успешно загружено, размер: {len(response.content)} байт")
    except Exception as e:
        logging.exception("❌ Ошибка при загрузке аудио")
        return None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp_file:
            tmp_file.write(response.content)
            temp_path = tmp_file.name

        logging.info(f"💾 Временный файл сохранён: {temp_path}")

        with open(temp_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                        model="gpt-4o-transcribe",
                        file=audio_file
                        )
            logging.info(f"📝 Распознанный текст: {transcript.text}")
            return transcript.text

    except Exception as e:
        logging.exception("❌ Ошибка при расшифровке аудио")
        return None
