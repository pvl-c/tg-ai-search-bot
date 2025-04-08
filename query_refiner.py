import openai
import json
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def refine_query(raw_text: str) -> dict:
    system_prompt = (
        "Ты AI-ассистент, который помогает структурировать запросы пользователей "
        "для подбора исполнителей (диджеев, фотографов, дизайнеров и т.д.). "
        "Извлеки из текста ключевые поля: роль, стиль, локация, событие, время, дополнительно. "
        "Если информация отсутствует — оставь поле пустым. Ответ верни в JSON-формате."
    )

    user_prompt = f"""Запрос: "{raw_text}"\n\nОтвети строго в JSON, вот пример:
{{
  "role": "диджей",
  "style": "хаус, рейв",
  "location": "Казань",
  "event": "вечеринка",
  "preferred_time": "вечером",
  "other": "нужен свой звук"
}}"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()

        # Попробуем загрузить как JSON
        return json.loads(content)

    except Exception as e:
        print("❌ Ошибка в refine_query:", e)
        return {}
