import telebot
import json
from flask import Flask
from threading import Thread
from config import BOT_TOKEN, ADMIN_ID, YOUTUBE_CHANNEL, TELEGRAM_GROUP, WEB_URL

bot = telebot.TeleBot(BOT_TOKEN)
data_file = "data.json"

# ---------------- Data Persistence ----------------
def load_data():
    try:
        with open(data_file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(data_file, "w") as f:
        json.dump(data, f)

users = load_data()

def check_user(user_id):
    if str(user_id) not in users:
        users[str(user_id)] = {"points": 0, "shares": 0, "ref": 0}
        save_data(users)

# ---------------- Config ----------------
REFERRAL_POINTS = 100
SHARE_POINTS = 25
SHARE_LIMIT = 5

# ---------------- Start Command ----------------
@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    check_user(user_id)

    # Referral System
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id != user_id:
            check_user(referrer_id)
            users[referrer_id]["points"] += REFERRAL_POINTS
            users[referrer_id]["ref"] += 1
            save_data(users)
            bot.send_message(referrer_id, f"🎉 नया यूज़र आपके लिंक से जुड़ा! आपको {REFERRAL_POINTS} कॉइन मिले ✅")

    # 🌐 Web + Invite Buttons
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("🌐 Web Open", url=WEB_URL),
        telebot.types.InlineKeyboardButton("👥 Invite", url=f"https://t.me/YOUR_BOT_USERNAME?start={user_id}")
    )

    bot.send_message(message.chat.id,
        f"👋 स्वागत है *BoomUp Bot* में, {message.from_user.first_name}!\n\n"
        f"👥 Invite करो → {REFERRAL_POINTS} कॉइन\n"
        f"🔄 शेयर करो → {SHARE_POINTS} कॉइन\n\n"
        f"📺 YouTube: {YOUTUBE_CHANNEL}\n"
        f"💬 Telegram: {TELEGRAM_GROUP}\n\n"
        f"👇 नीचे Menu से ऑप्शन चुनो 👇",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ---------------- Main Menu ----------------
def main_menu():
    menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row("🔄 शेयर करो", "📊 मेरे पॉइंट्स")
    menu.row("🔗 रेफ़रल लिंक", "🎁 प्रमोशन")
    return menu

# ---------------- Handle Messages ----------------
@bot.message_handler(func=lambda msg: True)
def handle_all(message):
    user_id = str(message.from_user.id)
    text = message.text
    check_user(user_id)

    # 🔄 Share
    if text == "🔄 शेयर करो":
        if users[user_id]["shares"] < SHARE_LIMIT:
            users[user_id]["shares"] += 1
            users[user_id]["points"] += SHARE_POINTS
            save_data(users)
            bot.reply_to(message, f"✅ शेयर सफल! {SHARE_POINTS} कॉइन मिले 🎉")
        else:
            bot.reply_to(message, f"⚠️ {SHARE_LIMIT} शेयर आज कर चुके हो। कल फिर ट्राय करो।")

    # 📊 Stats
    elif text == "📊 मेरे पॉइंट्स":
        u = users[user_id]
        bot.reply_to(message,
            f"📊 आपके Stats:\n\n"
            f"⭐ Total Points: {u['points']}\n"
            f"🔄 Shares: {u['shares']}/{SHARE_LIMIT}\n"
            f"👥 Referrals: {u['ref']}"
        )

    # 🔗 Referral Link
    elif text == "🔗 रेफ़रल लिंक":
        bot.reply_to(message,
            f"👉 आपका Referral Link:\n"
            f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
        )

    # 🎁 Promotion
    elif text == "🎁 प्रमोशन":
        if users[user_id]["points"] >= 1000:
            bot.reply_to(message, "✅ Send your YouTube/Promotion link. Admin approval के बाद 3 दिन तक प्रमोशन होगा।")
        else:
            bot.reply_to(message, f"⚠️ प्रमोशन के लिए 1000 कॉइन चाहिए। आपके पास {users[user_id]['points']} कॉइन हैं।")

# ---------------- Flask App for 24/7 ----------------
app = Flask("")

@app.route("/")
def home():
    return "BoomUp Invite Bot is running 24/7 ✅"

def run_flask():
    app.run(host="0.0.0.0", port=5000)

def run_bot():
    bot.infinity_polling()

# ---------------- Run Both ----------------
Thread(target=run_flask).start()
Thread(target=run_bot).start()