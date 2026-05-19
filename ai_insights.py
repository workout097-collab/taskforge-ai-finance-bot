import os
import httpx
from dotenv import load_dotenv
from database import get_expenses_db, get_currency_db, is_premium

load_dotenv()


async def get_ai_advice(user_id: int, language: str) -> str:
    """Генерує персоналізовану фінансову пораду через GPT"""

    if not is_premium(user_id):
        return "🔒 Ця функція доступна в Premium ($5/міс). Напиши /premium"

    expenses = get_expenses_db(user_id)
    if not expenses:
        return "Додай перші витрати командою /add Food 300"

    # Збираємо статистику
    stats = {}
    total = 0
    for e in expenses[-30:]:  # останні 30 днів
        cat = e[2]
        amount = e[3]
        total += amount
        stats[cat] = stats.get(cat, 0) + amount

    # Формуємо промпт
    prompt = f"""
Користувач витратив за місяць:
{stats}
Всього: {total} {get_currency_db(user_id)}

Дай коротку пораду (2-3 речення) мовою {language}:
- Що робити, щоб менше витрачати
- Де найбільша категорія витрат
- Мотивацію економити
"""

    # Використовуємо OpenAI API
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200
            }
        )
        data = response.json()

        # Додай перевірку на помилку
        if "error" in data:
            return f"❌ Помилка API: {data['error'].get('message', 'Невідома помилка')}"

        return data["choices"][0]["message"]["content"]