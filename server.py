import os
import threading
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, request

from telegram import Update
from telegram.ext import Application, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Leave empty at first

URL = "https://tickets.cafonline.com/fr"
CHECK_INTERVAL = 120  # 2 minutes

app = Flask(__name__)

telegram_app = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context):
    global CHAT_ID
    CHAT_ID = str(update.effective_chat.id)
    await update.message.reply_text("✅ Ticket alert activated!")
    print("CHAT_ID =", CHAT_ID)


telegram_app.add_handler(CommandHandler("start", start))


def check_tickets():
    """Runs in background every 2 minutes"""
    global CHAT_ID

    while True:
        try:
            resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text().lower()

            keywords = ["acheter", "buy", "tickets", "billets"]

            if any(k in text for k in keywords):
                if CHAT_ID:
                    telegram_app.bot.send_message(chat_id=CHAT_ID, text=f"🔥🎟️ Tickets AVAILABLE!\n{URL}")
                    time.sleep(3600)
        except Exception as e:
            print("Error:", e)

        time.sleep(CHECK_INTERVAL)


@app.post("/webhook")
def webhook():
    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, telegram_app.bot)
    telegram_app.update_queue.put(update)
    return "OK"


@app.get("/")
def home():
    return "Bot is running."


# Start background checker
threading.Thread(target=check_tickets, daemon=True).start()


if __name__ == "__main__":
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        url_path="/webhook",
        webhook_url=f"{os.getenv('RAILWAY_PUBLIC_URL')}/webhook"
    )
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
