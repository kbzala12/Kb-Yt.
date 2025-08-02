import telebot import time import sqlite3 from flask import Flask from threading import Thread

BOT_TOKEN = "8192810260:AAFfhjDfNywZIzkrlVmtAuKFL5_E-ZnsOmU" TELEGRAM_GROUP = "@boomupbot10" VIDEO_CODES = { "boom123": { "link": "https://youtu.be/QSH5mW7Il00", "id": "QSH5mW7Il00" }, "xpress456": { "link": "https://youtu.be/cDHi31m0rxI", "id": "cDHi31m0rxI" }, # More codes can be added here }

bot = telebot.TeleBot(BOT_TOKEN)

def is_user_in_group(user_id): try: member = bot.get_chat_member(TELEGRAM_GROUP, user_id) return member.status in ['member', 'creator', 'administrator'] except: return False

@bot.message_handler(commands=['start']) def start_message(message): user_id = message.from_user.id if not is_user_in_group(user_id): bot.send_message(message.chat.id, f"👋 Welcome!

🚨 पहले हमारे ग्रुप को जॉइन करें ताकि आप इनाम पा सकें: 👉 {TELEGRAM_GROUP}", parse_mode="Markdown") return bot.send_message(message.chat.id, "🎉 स्वागत है!

🎁 वीडियो देखो, कोड भेजो और इनाम पाओ!

👇 सभी वीडियो देखने के लिए /video लिखें")

@bot.message_handler(commands=['video']) def send_video_list(message): user_id = message.from_user.id if not is_user_in_group(user_id): bot.send_message(message.chat.id, f"🚫 पहले हमारे ग्रुप को जॉइन करें: 👉 {TELEGRAM_GROUP}") return

for code, data in VIDEO_CODES.items():
    video_link = data["link"]
    video_id = data["id"]
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
    caption = f"🎬 *वीडियो देखें और 3 मिनट बाद 🎁 इनाम पाएं!*

👉 कोड: {code}"

markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("▶️ वीडियो देखें", url=video_link))

    bot.send_photo(
        chat_id=message.chat.id,
        photo=thumbnail_url,
        caption=caption,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['watch']) def watch_video(message): bot.send_message(message.chat.id, "⏳ कृपया वीडियो देखें... 3 मिनट बाद 🎁 कोड भेजें।") time.sleep(180) bot.send_message(message.chat.id, "✅ अब आप 🎁 Reward के लिए कोड भेज सकते हैं!")

@bot.message_handler(func=lambda message: True) def handle_code(message): user_id = message.from_user.id if not is_user_in_group(user_id): bot.send_message(message.chat.id, f"🚫 पहले हमारे ग्रुप को जॉइन करें: 👉 {TELEGRAM_GROUP}") return

code = message.text.strip()
if code in VIDEO_CODES:
    bot.send_message(message.chat.id, "🎁 बधाई हो! आपने सही कोड भेजा है। इनाम भेजा जा रहा है।")
else:
    bot.send_message(message.chat.id, "❌ गलत कोड। कृपया सही कोड भेजें।")

Flask app for keep-alive

app = Flask('') @app.route('/') def home(): return "Bot is running!"

def run(): app.run(host='0.0.0.0', port=8080)

Thread(target=run).start() print("🤖 Bot is running...") bot.polling(none_stop=True)

