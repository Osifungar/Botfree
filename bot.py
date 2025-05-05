import telebot
from telebot import types
import json
import os
import requests

# === טוען את קובץ ההגדרות ===
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
TON_API = config["TON_API"]
DEFAULT_WALLET = config["DEFAULT_WALLET"]

bot = telebot.TeleBot(BOT_TOKEN)

# === ניהול ארנקים ===
wallets_file = "wallets.json"

def load_wallets():
    if not os.path.exists(wallets_file) or os.path.getsize(wallets_file) == 0:
        return {}
    with open(wallets_file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_wallets(data):
    with open(wallets_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

user_wallets = load_wallets()

# === /start ===
@bot.message_handler(commands=["start"])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔗 התחבר לארנק", callback_data="connect"),
        types.InlineKeyboardButton("💰 בדוק יתרה", callback_data="balance"),
        types.InlineKeyboardButton("📤 שלח כסף", callback_data="send"),
        types.InlineKeyboardButton("⚙️ הגדרות", callback_data="settings")
    )
    bot.send_message(message.chat.id, "👋 ברוך הבא לבוט ארנק טלגרם!\nבחר פעולה:", reply_markup=markup)

# === כפתורים ===
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    user_id = str(call.from_user.id)
    
    if call.data == "connect":
        bot.send_message(call.message.chat.id, "📥 אנא שלח את כתובת הארנק שלך (TON).")
        bot.register_next_step_handler(call.message, save_wallet_address)
    
    elif call.data == "balance":
        wallet = user_wallets.get(user_id, DEFAULT_WALLET)
        ton_balance = get_ton_balance(wallet)
        bot.send_message(call.message.chat.id, f"💰 יתרת הארנק שלך היא:\n{ton_balance} TON")
    
    elif call.data == "send":
        bot.send_message(call.message.chat.id, "📤 הפונקציה תתווסף בהמשך. (שליחת TON לארנק אחר)")
    
    elif call.data == "settings":
        bot.send_message(call.message.chat.id, "⚙️ כאן תוכל להגדיר העדפות נוספות (בהמשך).")

# === שמירת ארנק ===
def save_wallet_address(message):
    user_id = str(message.from_user.id)
    user_wallets[user_id] = message.text.strip()
    save_wallets(user_wallets)
    bot.send_message(message.chat.id, "✅ הארנק שלך נשמר בהצלחה!")

# === בדיקת יתרה ב-TON ===
def get_ton_balance(wallet_address):
    try:
        response = requests.get(f"{TON_API}/accounts/{wallet_address}")
        data = response.json()
        balance = int(data.get("balance", 0)) / 1e9  # TON מחושב ב-nanoTON
        return round(balance, 4)
    except Exception as e:
        return f"שגיאה: {e}"

print("🚀 הבוט עלה... מחכה להודעות")
bot.infinity_polling()
