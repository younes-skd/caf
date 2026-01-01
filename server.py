import os
import threading
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Leave empty initially
URL = "https://tickets.cafonline.com/fr"
CHECK_INTERVAL = 120  # 2 minutes

bot = Bot(BOT_TOKEN)
app = Flask(__name__)

dispatcher = Dispatcher(bot, None, workers=0)

def check_tickets():
    """Runs in background to check ticket availability"""
    global CHAT_ID
    while True:
        try:
            resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text().lower()

            keywords = ["acheter", "buy", "tickets", "billets"]

            if any(k in text for k in keywords):
                if CHAT_ID and CHAT_ID != "":
                    bot.send_message(CHAT_ID, f"🔥🎟️ Tickets AVAILABLE!\n{URL}")
                    time.sleep(3600)
        except Exception as e:
            print("Error:", e)

        time.sleep(CHECK_INTERVAL)


def start(update: Update, context):
    global CHAT_ID
    CHAT_ID = str(update.message.chat.id)
    bot.send_message(CHAT_ID, "✅ Ticket alert activated!")
    print("CHAT_ID =", CHAT_ID)


dispatcher.add_handler(CommandHandler("start", start))


@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"


@app.route("/")
def home():
    return "Bot is running."


# Launch background thread
threading.Thread(target=check_tickets, daemon=True).start()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # RAILWAY PORT
    app.run(host="0.0.0.0", port=port)
