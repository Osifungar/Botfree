import telebot
from telebot import types
import json
import requests
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

# טוען כתובות שמורות
def load_wallets():
    try:
        with open("wallets.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_wallets(wallets):
    with open("wallets.json", "w") as f:
        json.dump(wallets, f)

user_wallets = load_wallets()

# בדיקת יתרה מארנק TON דרך tonapi.io
def get_ton_balance(address):
    try:
        response = requests.get(f"https://tonapi.io/v1/account/{address}")
        data = response.json()
        balance = int(data["balance"]) / 1e9
        return round(balance, 4)
    except:
        return None

# תפריט ראשי
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔐 התחבר לארנק טלגרם", url="https://t.me/wallet"),
        types.InlineKeyboardButton("📤 שלח כתובת TON", callback_data="send_wallet"),
        types.InlineKeyboardButton("💰 בדוק יתרה", callback_data="check_balance"),
        types.InlineKeyboardButton("📘 למדו איך זה עובד", callback_data="learn"),
    )
    bot.send_message(message.chat.id, "👋 ברוך הבא לבוט שמנגיש את עולם הקריפטו דרך טלגרם!\nבחר פעולה:", reply_markup=markup)

# לחיצות על כפתורים
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    chat_id = str(call.message.chat.id)

    if call.data == "send_wallet":
        bot.send_message(call.message.chat.id, "📥 שלח את כתובת ה־TON שלך (מתחילה ב־UQC... או EQ...):")

    elif call.data == "check_balance":
        address = user_wallets.get(chat_id)
        if not address:
            bot.send_message(call.message.chat.id, "⚠️ לא נמצאה כתובת. לחץ שוב על '📤 שלח כתובת TON'")
            return

        bot.send_message(call.message.chat.id, "⏳ בודק יתרה...")
        balance = get_ton_balance(address)
        if balance is not None:
            bot.send_message(call.message.chat.id, f"💰 היתרה שלך: {balance} TON")
        else:
            bot.send_message(call.message.chat.id, "❌ שגיאה בבדיקת יתרה. ודא שהכתובת נכונה.")

    elif call.data == "learn":
        text = (
            "📘 *שימוש בארנק טלגרם להעברת כספים*\n\n"
            "בישראל, אין חובת דיווח על כל פעולה בקריפטו – רק *בעת מימוש* (למשל המרה לשקלים).\n\n"
            "➕ כאשר אתה שולח TON למשתמש אחר בטלגרם, לא מתבצע מימוש לפיאט\n"
            "📤 לכן זו העברה פרטית, ללא מיסוי מיידי\n"
            "📊 כך ניתן לנהל קהילה, לתגמל משתמשים, ולהעביר ערך בלי חשש ממס.\n\n"
            "_מידע זה אינו מהווה ייעוץ מס. לשימוש חינוכי בלבד._"
        )
        bot.send_message(call.message.chat.id, text, parse_mode='Markdown')

# קבלת כתובת מהמשתמש
@bot.message_handler(func=lambda message: message.text.startswith("UQC") or message.text.startswith("EQ"))
def save_wallet(message):
    chat_id = str(message.chat.id)
    address = message.text.strip()

    if 48 <= len(address) <= 64:
        user_wallets[chat_id] = address
        save_wallets(user_wallets)
        bot.send_message(chat_id, "✅ כתובת נשמרה בהצלחה!")
    else:
        bot.send_message(chat_id, "❌ כתובת לא תקינה. ודא שהיא מתחילה ב־UQC או EQ וכוללת לפחות 48 תווים.")

print("🤖 הבוט מחכה להודעות...")
bot.infinity_polling()
