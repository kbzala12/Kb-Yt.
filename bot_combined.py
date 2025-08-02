import telebot, sqlite3, os
from flask import Flask
from threading import Thread

# ========== CONFIG ==========
BOT_TOKEN = "8324637176:AAFeKHN29fpeGA4b7w5RfvSgrOH8LRkCYmY"
ADMIN_ID = 7459795138
TELEGRAM_GROUP = "@boomupbot10"

VIDEO_CODES = {
    "boom123": "https://youtu.be/QSH5mW7Il00?si=AcLkdNBNSJqGs5y3",
    "xpress456": "https://youtu.be/cDHi31m0rxI?si=xHUXL54PjtFS-wlN",
    "kzboom789": "https://youtu.be/k84NTqHakEE?si=q_1FZRrIdjPjWZKa",
    "flash321": "https://youtu.be/wskpFAMrb6I?si=cx4bYzmwBgY68Qmq",
    "hindi007": "https://youtu.be/smWCVRNMqh0?si=hBmNoBIMyLLKCoM2"
}
import threading

@bot.message_handler(func=lambda msg: msg.text == "🎥 वीडियो देखा")
def handle_video_watch(message):
    user_id = str(message.from_user.id)
    check_user(user_id)

    msg = (
        "🎬 *नीचे वीडियो लिस्ट है:*\n\n"
        "1. [🔥 वीडियो 1](https://youtu.be/QSH5mW7Il00?si=AcLkdNBNSJqGs5y3)\n"
        "2. [🚀 वीडियो 2](https://youtu.be/cDHi31m0rxI?si=xHUXL54PjtFS-wlN)\n"
        "3. [🎯 वीडियो 3](https://youtu.be/k84NTqHakEE?si=q_1FZRrIdjPjWZKa)\n"
        "4. [🎥 वीडियो 4](https://youtu.be/wskpFAMrb6I?si=cx4bYzmwBgY68Qmq)\n"
        "5. [🔥 वीडियो 5](https://youtu.be/smWCVRNMqh0?si=hBmNoBIMyLLKCoM2)\n\n"
        "⏳ *हर वीडियो को कम से कम 4 मिनट देखें*।"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

    # 🔁 4 मिनट (240 सेकंड) बाद कोड डालने की अनुमति वाला मैसेज भेजें
    def send_code_prompt():
        bot.send_message(
            message.chat.id,
            "🕓 अब आप कोड डाल सकते हैं (जैसे: `boom123`)",
            parse_mode="Markdown"
        )

    threading.Timer(240, send_code_prompt).start()  # 240 sec = 4 min
# ========== KEEP ALIVE ==========
app = Flask('')
@app.route('/')
def home(): return "Bot is running"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()
keep_alive()

# ========== DATABASE SETUP ==========
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    points INTEGER DEFAULT 0,
    videos INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    ref INTEGER DEFAULT 0,
    referred_by TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS redemptions (
    id TEXT,
    code TEXT,
    UNIQUE(id, code)
)
""")
conn.commit()

# ========== DB FUNCTIONS ==========
def check_user(user_id):
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
        conn.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return {"id": row[0], "points": row[1], "videos": row[2], "shares": row[3], "ref": row[4], "referred_by": row[5]} if row else None

def add_points(user_id, field, max_limit, increment, points):
    cursor.execute(f"SELECT {field}, points FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if row and row[0] < max_limit:
        cursor.execute(f"UPDATE users SET {field} = {field} + ?, points = points + ? WHERE id = ?", (increment, points, user_id))
        conn.commit()
        return True
    return False

def apply_referral(new_user_id, ref_id):
    if new_user_id == ref_id: return
    user = get_user(new_user_id)
    if user["referred_by"]: return
    if get_user(ref_id):
        cursor.execute("UPDATE users SET ref = ref + 1, points = points + 50 WHERE id = ?", (ref_id,))
        cursor.execute("UPDATE users SET referred_by = ? WHERE id = ?", (ref_id, new_user_id))
        conn.commit()

# ========== TELEGRAM BOT ==========
bot = telebot.TeleBot(BOT_TOKEN)

def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(TELEGRAM_GROUP, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error: {e}")
        return False

def main_menu():
    menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row("🎥 वीडियो देखा", "📤 शेयर किया")
    menu.row("📊 मेरी जानकारी", "🔗 रेफरल लिंक")
    menu.row("🎯 प्रमोशन सबमिट")
    return menu

@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)

    if not is_user_in_channel(user_id):
        join_btn = telebot.types.InlineKeyboardMarkup()
        join_btn.add(telebot.types.InlineKeyboardButton("📥 ग्रुप जॉइन करें", url=f"https://t.me/{TELEGRAM_GROUP.replace('@', '')}"))
        bot.send_message(message.chat.id, "🚫 पहले हमारे Telegram Group को जॉइन करें:", reply_markup=join_btn)
        return

    check_user(user_id)

    if len(message.text.split()) > 1:
        ref_id = message.text.split()[1]
        apply_referral(user_id, ref_id)

    # ✅ Welcome Message Without Image
    bot.send_message(
        message.chat.id,
        "👋 *Welcome to BoomUp Bot!*\n\n🎥 वीडियो देखो, कोड डालो और पॉइंट्स कमाओ!\n📤 शेयर करो, रेफर करो और प्रमोशन का मौका पाओ!\n\n💡 वीडियो देखकर अंत में दिखा कोड मुझे भेजें।",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda msg: True)
def handle_all(message):
    user_id = str(message.from_user.id)
    check_user(user_id)
    text = message.text

    if text == "🎥 वीडियो देखा":
        msg = "🎥 ये वीडियो देखिए और अंत में दिखा *code* मुझे भेजिए:\n\n"
        for code, link in VIDEO_CODES.items():
            msg += f"🔗 {link}\n"
        bot.reply_to(message, msg, parse_mode="Markdown")

    elif text == "📤 शेयर किया":
        if add_points(user_id, "shares", 5, 1, 25):
            bot.reply_to(message, "✅ शेयर करने के लिए धन्यवाद, +25 पॉइंट्स!")
        else:
            bot.reply_to(message, "❌ आपने 5 शेयर की लिमिट पूरी कर ली है।")

    elif text == "📊 मेरी जानकारी":
        u = get_user(user_id)
        bot.reply_to(message, f"""📊 आपकी जानकारी:
Total Points: {u['points']}
🎥 Videos: {u['videos']}/10
📤 Shares: {u['shares']}/5
🔗 Referrals: {u['ref']}""")

    elif text == "🔗 रेफरल लिंक":
        bot.reply_to(message, f"🔗 आपका रेफरल लिंक:\nhttps://t.me/NewYt1_bot?start={user_id}")

    elif text == "🎯 प्रमोशन सबमिट":
        u = get_user(user_id)
        if u['points'] >= 1000:
            bot.reply_to(message, "✅ कृपया अपना प्रमोशन लिंक भेजें:")
        else:
            bot.reply_to(message, "❌ प्रमोशन के लिए 1000 पॉइंट्स ज़रूरी हैं।")

@bot.message_handler(func=lambda m: m.text.lower() in VIDEO_CODES)
def handle_secret_code(message):
    user_id = str(message.from_user.id)
    code = message.text.lower()
    cursor.execute("SELECT id FROM redemptions WHERE id = ? AND code = ?", (user_id, code))
    if cursor.fetchone():
        bot.reply_to(message, "⚠️ आपने ये कोड पहले ही इस्तेमाल किया है।")
        return

    if add_points(user_id, "videos", 10, 1, 10):
        cursor.execute("INSERT INTO redemptions (id, code) VALUES (?, ?)", (user_id, code))
        conn.commit()
        bot.reply_to(message, "✅ सही कोड! आपको 10 पॉइंट्स मिले 🎉")
    else:
        bot.reply_to(message, "⚠️ आपने पहले ही 10 वीडियो पूरे कर लिए हैं।")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    action, user_id = call.data.split(":")
    if action == "approve":
        bot.send_message(user_id, "✅ आपका लिंक अप्रूव हो गया है! 3 दिन तक लाइव रहेगा.")
    elif action == "reject":
        bot.send_message(user_id, "❌ आपका प्रमोशन लिंक reject कर दिया गया है.")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

print("🤖 Bot is running...")
bot.infinity_polling()