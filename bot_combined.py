# bot.py
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import time
import threading
import requests

# --- Config ---
BOT_TOKEN = "8267991203:AAH7-oOq-qKAed4OSBQdMxlg-UDCVZLyzF0"
ADMIN_ID = 7459795138
GROUP_USERNAME = "boomupbot10"  # '@' के बिना

bot = telebot.TeleBot(BOT_TOKEN)

# --- Database Setup ---
conn = sqlite3.connect("botdata.db", check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 0
)""")
c.execute("""CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id TEXT
)""")
conn.commit()

# --- Helper Functions ---
def is_user_in_group(user_id):
    try:
        res = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember",
            params={"chat_id": f"@{GROUP_USERNAME}", "user_id": user_id}
        ).json()
        status = res["result"]["status"]
        return status in ["member", "administrator", "creator"]
    except Exception:
        return False

def add_coins(user_id, amount):
    c.execute("INSERT OR IGNORE INTO users (telegram_id, coins) VALUES (?, 0)", (user_id,))
    c.execute("UPDATE users SET coins = coins + ? WHERE telegram_id=?", (amount, user_id))
    conn.commit()

def get_coins(user_id):
    c.execute("SELECT coins FROM users WHERE telegram_id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 0

# --- Commands ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if is_user_in_group(uid):
        bot.send_message(uid, "✅ Welcome! आप group member हैं.\n/videos से videos देखें.")
    else:
        join_markup = InlineKeyboardMarkup()
        join_markup.add(InlineKeyboardButton("🚀 Group Join करें", url=f"https://t.me/{GROUP_USERNAME}"))
        bot.send_message(uid, "❌ पहले group join करें, फिर /start भेजें.", reply_markup=join_markup)

@bot.message_handler(commands=['addvideo'])
def addvideo(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ केवल admin वीडियो जोड़ सकता है.")
        return
    bot.reply_to(message, "कृपया वीडियो भेजें.")
    bot.register_next_step_handler(message, save_video)

def save_video(message):
    if message.video:
        fid = message.video.file_id
        c.execute("INSERT INTO videos (file_id) VALUES (?)", (fid,))
        conn.commit()
        bot.reply_to(message, "✅ वीडियो saved.")
    else:
        bot.reply_to(message, "❌ कृपया एक वीडियो भेजें.")

@bot.message_handler(commands=['videos'])
def list_videos(message):
    uid = message.from_user.id
    if not is_user_in_group(uid):
        join_markup = InlineKeyboardMarkup()
        join_markup.add(InlineKeyboardButton("🚀 Group Join करें", url=f"https://t.me/{GROUP_USERNAME}"))
        bot.send_message(uid, "❌ पहले group join करें, फिर /videos भेजें.", reply_markup=join_markup)
        return

    c.execute("SELECT id, file_id FROM videos")
    videos = c.fetchall()
    if not videos:
        bot.send_message(uid, "📭 कोई वीडियो नहीं है.")
        return

    for vid in videos:
        vid_id, file_id = vid
        watch_btn = InlineKeyboardMarkup()
        watch_btn.add(InlineKeyboardButton("✅ देखा", callback_data=f"watch_{vid_id}"))
        bot.send_video(uid, file_id, reply_markup=watch_btn)

@bot.callback_query_handler(func=lambda call: call.data.startswith("watch_"))
def watched(call):
    uid = call.from_user.id
    vid_id = call.data.split("_")[1]
    bot.answer_callback_query(call.id, "⏳ 3 मिनट इंतजार करें coins पाने के लिए...")

    def delayed_add():
        time.sleep(180)  # 3 मिनट
        add_coins(uid, 10)
        bot.send_message(uid, f"🎉 आपने 10 coins कमा लिए!\n💰 Total coins: {get_coins(uid)}")

    threading.Thread(target=delayed_add).start()

@bot.message_handler(commands=['coins'])
def coins(message):
    uid = message.from_user.id
    bot.send_message(uid, f"💰 आपके coins: {get_coins(uid)}")

# --- Run Bot ---
bot.infinity_polling()