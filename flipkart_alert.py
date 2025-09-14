import os
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========== CONFIG ==========
PRODUCT_URL = os.getenv("PRODUCT_URL", "https://www.flipkart.com/")
TARGET_PRICE = int(os.getenv("TARGET_PRICE", "34000"))

# Twilio credentials from env
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
TO_WHATSAPP_NUMBER = os.getenv("TO_WHATSAPP_NUMBER")

# ========== SCRAPER ==========
def get_price():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(PRODUCT_URL, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Flipkart price container
    price_tag = soup.find("div", {"class": "Nx9bqj CxhGGd"})
    if not price_tag:
        raise Exception("Price element not found. Selector might have changed.")

    price = int(price_tag.text.replace("₹", "").replace(",", "").strip())
    return price

# ========== WHATSAPP SENDER ==========
def send_whatsapp(current_price):
    diff = TARGET_PRICE - current_price
    note = f"🎉 It's ₹{abs(diff)} cheaper than your target!"

    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(
        body=f"🔥 Flipkart Price Alert!\n"
             f"Current Price: ₹{current_price}\n"
             f"Target Price: ₹{TARGET_PRICE}\n"
             f"{note}\n\n"
             f"Check here: {PRODUCT_URL}",
        from_=TWILIO_WHATSAPP_NUMBER,
        to=TO_WHATSAPP_NUMBER
    )
    print("📲 WhatsApp message sent! SID:", message.sid)

# ========== MAIN ==========
if __name__ == "__main__":
    try:
        price = get_price()
        print(f"Current Price: ₹{price}")

        if price < TARGET_PRICE:
            print("✅ Price dropped! Sending WhatsApp...")
            send_whatsapp(price)
        else:
            print("❌ Price still high. No notification sent.")
    except Exception as e:
        print("Error:", e)
