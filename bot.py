import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Loaded automatically after /start

URL = "https://tickets.cafonline.com/fr"
CHECK_INTERVAL = 120  # 2 minutes

bot = Bot(token=BOT_TOKEN)


def check_tickets():
    """Scrape CAF website for ticket keywords."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(URL, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text().lower()

        keywords = ["acheter", "tickets", "billets", "buy"]
        return any(k in text for k in keywords)

    except Exception as e:
        print("Scraper error:", e)
        return False


# STEP 1 — Wait for /start
if not CHAT_ID:
    print("Waiting for /start message...")

    last_update_id = None
    while True:
        try:
            updates = bot.get_updates(offset=last_update_id, timeout=10)
        except Exception as e:
            print("Polling error:", e)
            time.sleep(2)
            continue

        for u in updates:
            last_update_id = u.update_id + 1

            if u.message and u.message.text.strip() == "/start":
                chat_id = u.message.chat.id
                bot.send_message(chat_id=chat_id,
                                 text="Ticket alert activated! I will notify you.")
                print("CHAT_ID received:", chat_id)

                # Save chat id for next restart
                with open(".env", "a") as f:
                    f.write(f"\nCHAT_ID={chat_id}")

                CHAT_ID = str(chat_id)
                break

        if CHAT_ID:
            break

        time.sleep(1)


# STEP 2 — Main monitoring loop
print("Monitoring started...")

while True:
    try:
        if check_tickets():
            bot.send_message(
                chat_id=CHAT_ID,
                text=f"🔥🎟️ Tickets AVAILABLE!\n{URL}"
            )
            time.sleep(3600)  # Avoid spam
    except Exception as e:
        print("Loop error:", e)

    time.sleep(CHECK_INTERVAL)
