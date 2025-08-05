import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
import requests

BOT_TOKEN = "8192810260:AAFfhjDfNywZIzkrlVmtAuKFL5_E-ZnsOmU"
bot = telebot.TeleBot(BOT_TOKEN)

WEBAPP_URL = "https://hkyt-bot.onrender.com"
TELEGRAM_GROUP_USERNAME = "boomupbot10"  # 👉 बिना '@' के group username

ADMIN_CHAT_ID = 7470248597  # For debugging/logging if needed

# Function to check membership
def is_user_in_group(user_id):
    try:
        res = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{TELEGRAM_GROUP_USERNAME}&user_id={user_id}"
        ).json()
        status = res['result']['status']
        return status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if is_user_in_group(user_id):
        # ✅ Group joined → Show WebApp Button inside Telegram
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        webapp_button = KeyboardButton("🎁 वेब ऐप खोलें", web_app=WebAppInfo(url=WEBAPP_URL))
        markup.add(webapp_button)

        bot.send_message(message.chat.id, "✅ आपने ग्रुप जॉइन कर लिया है!\nनीचे दिए गए बटन से WebApp खोलें:", reply_markup=markup)

    else:
        # ❌ Not joined → Show Join Group Button
        join_markup = InlineKeyboardMarkup()
        join_button = InlineKeyboardButton("🚀 ग्रुप जॉइन करें", url=f"https://t.me/{TELEGRAM_GROUP_USERNAME}")
        join_markup.add(join_button)

        bot.send_message(message.chat.id,
                         "❌ आप अभी हमारे ऑफिशियल ग्रुप में नहीं हैं!\nकृपया पहले नीचे दिए गए बटन से ग्रुप जॉइन करें फिर /start भेजें।",
                         reply_markup=join_markup)

bot.infinity_polling()