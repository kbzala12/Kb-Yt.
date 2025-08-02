import telebot, sqlite3, threading from flask import Flask from threading import Thread from keep_alive import keep_alive

========== CONFIG ==========

BOT_TOKEN = "8192810260:AAFfhjDfNywZIzkrlVmtAuKFL5_E-ZnsOmU"  
 ADMIN_ID = 7459795138 TELEGRAM_GROUP = "@boomupbot10"

VIDEO_CODES = { "boom123": "https://youtu.be/QSH5mW7Il00?si=AcLkdNBNSJqGs5y3", "xpress456": "https://youtu.be/cDHi31m0rxI?si=xHUXL54PjtFS-wlN", "kzboom789": "https://youtu.be/k84NTqHakEE?si=q_1FZRrIdjPjWZKa", "flash321": "https://youtu.be/wskpFAMrb6I?si=cx4bYzmwBgY68Qmq", "hindi007": "https://youtu.be/smWCVRNMqh0?si=hBmNoBIMyLLKCoM2" }

bot = telebot.TeleBot(BOT_TOKEN)

========== KEEP ALIVE ==========

keep_alive()

========== DATABASE SETUP ==========

conn = sqlite3.connect("bot.db", check_same_thread=False) cursor = conn.cursor()

cursor.execute(""" CREATE TABLE IF NOT EXISTS users ( id TEXT PRIMARY KEY, points INTEGER DEFAULT 0, videos INTEGER DEFAULT 0, shares INTEGER DEFAULT 0, ref INTEGER DEFAULT 0, referred_by TEXT ) """)

cursor.execute(""" CREATE TABLE IF NOT EXISTS redemptions ( id TEXT, code TEXT, UNIQUE(id, code) ) """)

conn.commit()

========== DB FUNCTIONS ==========

def check_user(user_id): cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,)) if not cursor.fetchone(): cursor.execute("INSERT INTO users (id) VALUES (?)", (user_id,)) conn.commit()

def get_user(user_id): cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) row = cursor.fetchone() return {"id": row[0], "points": row[1], "videos": row[2], "shares": row[3], "ref": row[4], "referred_by": row[5]} if row else None

def add_points(user_id, field, max_limit, increment, points): cursor.execute(f"SELECT {field}, points FROM users WHERE id = ?", (user_id,)) row = cursor.fetchone() if row and row[0] < max_limit: cursor.execute(f"UPDATE users SET {field} = {field} + ?, points = points + ? WHERE id = ?", (increment, points, user_id)) conn.commit() return True return False

def apply_referral(new_user_id, ref_id): if new_user_id == ref_id: return cursor.execute("SELECT id FROM users WHERE id = ?", (ref_id,)) if cursor.fetchone(): cursor.execute("UPDATE users SET ref = ref + 1, points = points + 5 WHERE id = ?", (ref_id,)) cursor.execute("UPDATE users SET referred_by = ? WHERE id = ?", (ref_id, new_user_id)) conn.commit()

========== HANDLERS ==========

@bot.message_handler(commands=['start']) def handle_start(message): user_id = str(message.from_user.id) first_time = False cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,)) if not cursor.fetchone(): check_user(user_id) first_time = True

if " " in message.text:
    ref_id = message.text.split()[1]
    apply_referral(user_id, ref_id)

reply = (
    f"👋 स्वागत है! आप वीडियो देखकर और अपने दोस्तों को रेफर करके पॉइंट कमा सकते हैं!\n\n"
    f"🎁 अपने पॉइंट चेक करने के लिए टाइप करें: /mypoints\n"
    f"👥 रेफरल लिंक: https://t.me/{bot.get_me().username}?start={user_id}"
)

bot.reply_to(message, reply)

if first_time:
    bot.send_message(message.chat.id, "🎥 वीडियो देखने के लिए '🎥 वीडियो देखा' भेजें")

@bot.message_handler(commands=['mypoints']) def handle_points(message): user_id = str(message.from_user.id) check_user(user_id) user = get_user(user_id) bot.reply_to(message, f"💰 आपके पॉइंट्स: {user['points']}\n" f"🎥 देखे गए वीडियो: {user['videos']}\n" f"👥 रेफरल्स: {user['ref']}")

@bot.message_handler(func=lambda msg: msg.text == "🎥 वीडियो देखा") def handle_video_watch(message): user_id = str(message.from_user.id) check_user(user_id)

msg = (
    "🎬 *नीचे वीडियो लिस्ट है:*\n\n"
    "1. [🔥 वीडियो 1](https://youtu.be/QSH5mW7Il00?si=AcLkdNBNSJqGs5y3)\n"
    "2. [🚀 वीडियो 2](https://youtu.be/cDHi31m0rxI?si=xHUXL54PjtFS-wlN)\n"
    "3. [🎯 वीडियो 3](https://youtu.be/k84NTqHakEE?si=q_1FZRrIdjPjWZKa)\n"
    "4. [🎥 वीडियो 4](https://youtu.be/wskpFAMrb6I?si=cx4bYzmwBgY68Qmq)\n"
    "5. [🔥 वीडियो 5](https://youtu.be/smWCVRNMqh0?si=hBmNoBIMyLLKCoM2)\n\n"
    "⏳ *हर वीडियो को कम से कम 4 मिनट देखें।*"
)
bot.reply_to(message, msg, parse_mode="Markdown")

def send_code_prompt():
    bot.send_message(message.chat.id, "🕓 अब आप कोड डाल सकते हैं (जैसे: `boom123`)", parse_mode="Markdown")

threading.Timer(240, send_code_prompt).start()

@bot.message_handler(func=lambda msg: msg.text.lower() in VIDEO_CODES) def handle_code_entry(message): user_id = str(message.from_user.id) code = message.text.lower() check_user(user_id)

cursor.execute("SELECT 1 FROM redemptions WHERE id = ? AND code = ?", (user_id, code))
if cursor.fetchone():
    bot.reply_to(message, "⚠️ आपने यह कोड पहले ही इस्तेमाल कर लिया है।")
    return

if code in VIDEO_CODES:
    success = add_points(user_id, "videos", 10, 1, 3)
    if success:
        cursor.execute("INSERT INTO redemptions (id, code) VALUES (?, ?)", (user_id, code))
        conn.commit()
        bot.reply_to(message, f"✅ कोड मान्य है! आपको 3 पॉइंट्स मिले।")
    else:
        bot.reply_to(message, "⚠️ आप 10 से अधिक वीडियो पर पॉइंट्स नहीं कमा सकते।")
else:
    bot.reply_to(message, "❌ गलत कोड!")

========== START BOT ==========

print("🤖 Bot is running...") bot.polling()

