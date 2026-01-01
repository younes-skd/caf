import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # leave empty on first deploy

URL = "https://tickets.cafonline.com/fr"
CHECK_INTERVAL = 120  # seconds

bot = Bot(token=BOT_TOKEN)

def check_tickets():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text().lower()

        keywords = ["acheter", "billet", "tickets", "buy"]
        return any(k in text for k in keywords)

    except Exception as e:
        print("Error checking page:", e)
        return False


# Wait for user to send /start
if not CHAT_ID:
    print("Waiting for /start message...")

    last_update_id = None
    while True:
        updates = bot.get_updates(offset=last_update_id, timeout=10)
        for u in updates:
            last_update_id = u.update_id + 1

            if u.message and u.message.text == "/start":
                chat_id = u.message.chat.id
                bot.send_message(chat_id=chat_id, text="Ticket alert activated! I will notify you.")
                print("CHAT_ID received:", chat_id)

                # store chat id for persistence
                with open(".env", "a") as f:
                    f.write(f"\nCHAT_ID={chat_id}")

                CHAT_ID = str(chat_id)
                break

        if CHAT_ID:
            break

        time.sleep(1)


# Main monitoring loop
while True:
    try:
        if check_tickets():
            bot.send_message(chat_id=CHAT_ID, text="🔥🎟️ Tickets AVAILABLE!\n" + URL)
            time.sleep(3600)  # avoid spam
    except Exception as e:
        print("Loop error:", e)

    time.sleep(CHECK_INTERVAL)
