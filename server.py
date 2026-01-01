import os
import threading
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Set after first /start
URL = "https://tickets.cafonline.com/fr"
CHECK_INTERVAL = 120  # seconds

bot = Bot(BOT_TOKEN)
app = Flask(__name__)

dispatcher = Dispatcher(bot, None, workers=0)

def check_tickets():
    """Checks ticket availability every 2 minutes"""
    global CHAT_ID
    while True:
        try:
            resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text().lower()

            keywords = ["acheter", "buy", "tickets", "billets"]

            if any(k in text for k in keywords):
                if CHAT_ID:
                    bot.send_message(CHAT_ID, f"🔥🎟️ Tickets AVAILABLE!\n{URL}")
                    time.sleep(3600)
        except Exception as e:
            print("Error:", e)

        time.sleep(CHECK_INTERVAL)


def start(update: Update, context):
    global CHAT_ID
    CHAT_ID = update.message.chat.id
    bot.send_message(CHAT_ID, "✅ Ticket alert activated!")
    print("CHAT_ID =", CHAT_ID)


dispatcher.add_handler(CommandHandler("start", start))


@app.route(f"/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"


# Start background thread on startup
threading.Thread(target=check_tickets, daemon=True).start()


@app.route("/")
def home():
    return "Bot running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
