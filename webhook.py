from fastapi import FastAPI, Request
import stripe
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

DATABASE = "expenses.db"

# Ця функція оновлює статус Premium в базі даних
def activate_premium(telegram_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE premium_users SET premium = 1, trial_end = '2099-12-31' WHERE user_id = ?",
        (telegram_id,)
    )
    conn.commit()
    conn.close()
    print(f"✅ Premium активовано для {telegram_id}")

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except Exception as e:
        print(f"❌ Помилка верифікації вебхука: {e}")
        return {"error": str(e)}

    # Обробка успішної оплати
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        telegram_id = session.get("client_reference_id")

        if telegram_id:
            activate_premium(int(telegram_id))
        else:
            print("⚠️ Отримано вебхук без client_reference_id")

    # Додаткові типи подій можна додати тут за потреби
    # elif event["type"] == "invoice.paid":
    #     # Обробка для підписок з автоматичним продовженням
    #     pass

    return {"status": "ok"}