import logging
import os
from flask import Flask, request as flask_request
import requests

# إعدادات الـ Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "9257361616:AAFtR4Cq-9-3bPMIEoAVK5em-2HoYUSAuio"
RENDER_URL = "https://texas4win-1.onrender.com"
ADMIN_TELEGRAM_ID = "7383417915"  # الأيدي الخاص بك لاستقبال الطلبات

app = Flask(__name__)

# قاعدة بيانات باقات الشدات والمنتجات داخل البوت
PRODUCTS_DB = {
    "buy_60": {"name": "📦 باقة 60 شدة (UC)", "price": "143,899 ليرة سورية", "item_id": "60"},
    "buy_325": {"name": "📦 باقة 325 شدة (UC)", "price": "700,000 ليرة سورية", "item_id": "325"},
    "buy_660": {"name": "📦 باقة 660 شدة (UC)", "price": "1,400,000 ليرة سورية", "item_id": "660"},
}

# متغير مؤقت لحفظ اختيار المستخدم (لربط الآيدي مع الباقة المختارة)
USER_STATE = {}


def send_telegram_message(chat_id, text, reply_markup=None):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {
      "chat_id": chat_id,
      "text": text,
      "parse_mode": "Markdown",
  }
  if reply_markup:
    payload["reply_markup"] = reply_markup
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    logger.error(f"Telegram Send Error: {e}")


def edit_telegram_message(chat_id, message_id, text, reply_markup=None):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
  payload = {
      "chat_id": chat_id,
      "message_id": message_id,
      "text": text,
      "parse_mode": "Markdown",
  }
  if reply_markup:
    payload["reply_markup"] = reply_markup
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    logger.error(f"Telegram Edit Error: {e}")


@app.route("/")
def home():
  return "One Store Order Management Bot is running perfectly!"


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
  try:
    data = flask_request.get_json(force=True)
    
    # معالجة الرسائل النصية (مثل الأوامر أو إدخال الآيدي)
    if "message" in data:
      msg = data["message"]
      chat_id = msg["chat"]["id"]
      user_name = msg.get("from", {}).get("first_name", "صديقي")
      text = msg.get("text", "")

      if text.startswith("/start"):
        # مسح أي حالة سابقة للمستخدم
        if chat_id in USER_STATE:
          del USER_STATE[chat_id]

        welcome_msg = (
            f"أهلاً بك يا أسطورة {user_name} في متجر الشحن الرسمي 🎮🔥\n\n"
            "اختر من الأزرار بالأسفل لتصفح باقات الشدات المطلوبة:"
        )
        keyboard = {
            "inline_keyboard": [
                [{"text": "🛒 تصفح باقات الشدات", "callback_data": "fetch_live_data"}],
                [{"text": "📞 التواصل والدعم", "callback_data": "support"}]
            ]
        }
        send_telegram_message(chat_id, welcome_msg, keyboard)

      # إذا كان المستخدم في حالة إدخال الآيدي (Player ID) بعد اختيار الباقة
      elif chat_id in USER_STATE:
        selected_product_key = USER_STATE[chat_id]
        product = PRODUCTS_DB[selected_product_key]
        player_id = text.strip()

        # إزالة حالة المستخدم بعد استلام الآيدي
        del USER_STATE[chat_id]

        # رسالة تأكيد للزبون
        confirmation_msg = (
            f"✅ تم استلام طلبك بنجاح يا أسطورة!\n\n"
            f"📦 المنتج: *{product['name']}*\n"
            f"💰 السعر: *{product['price']}*\n"
            f"🆔 آيدي اللاعب: `{player_id}`\n\n"
            "يرجى تحويل المبلغ عبر (شام كاش) وإرسال صورة الإيصال هنا، وسيتم تنفيذ الشحن فوراً!"
        )
        send_telegram_message(chat_id, confirmation_msg)

        # إرسال تفاصيل الطلب فوراً إلى حسابك (الإدمن) على تليجرام
        admin_notification = (
            f"🚨 *طلب شراء جديد وصلك!* 🚨\n\n"
            f"👤 اسم المستخدم: {user_name}\n"
            f"💬 معرف المستخدم: ` {chat_id} `\n"
            f"📦 الباقة المطلوبة: *{product['name']}*\n"
            f"💰 السعر: *{product['price']}*\n"
            f"🆔 آيدي اللاعب للشحن: `{player_id}`"
        )
        send_telegram_message(ADMIN_TELEGRAM_ID, admin_notification)

    # معالجة ضغطات الأزرار (Callback Queries)
    elif "callback_query" in data:
      query = data["callback_query"]
      chat_id = query["message"]["chat"]["id"]
      message_id = query["message"]["message_id"]
      callback_data = query["data"]

      requests.post(
          f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
          json={"callback_query_id": query["id"]},
          timeout=5
      )

      if callback_data == "fetch_live_data":
        inline_keyboard = []
        for key, prod in PRODUCTS_DB.items():
          inline_keyboard.append([{"text": f"{prod['name']} - {prod['price']}", "callback_data": key}])

        inline_keyboard.append([{"text": "🔙 رجوع للقائمة الرئيسية", "callback_data": "main_menu"}])
        
        edit_telegram_message(
            chat_id,
            message_id,
            "📂 قائمة الباقات المتوفرة في متجرك:\nاختر الباقة المطلوبة للشحن:",
            {"inline_keyboard": inline_keyboard}
        )

      elif callback_data in PRODUCTS_DB:
        # حفظ اختيار الباقة للمستخدم ليقوم بإدخال الآيدي بعدها
        USER_STATE[chat_id] = callback_data
        prod = PRODUCTS_DB[callback_data]

        prompt_msg = (
            f" لقد اخترت: *{prod['name']}*\n"
            f" السعر: *{prod['price']}*\n\n"
            "👇 **الرجاء إرسال الآيدي (Player ID) الخاص بك في لعبة PUBG Mobile الآن بالدردشة:**"
        )
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔙 عودة لقائمة الباقات", "callback_data": "fetch_live_data"}],
                [{"text": "🏠 القائمة الرئيسية", "callback_data": "main_menu"}]
            ]
        }
        edit_telegram_message(chat_id, message_id, prompt_msg, keyboard)

      elif callback_data == "main_menu":
        if chat_id in USER_STATE:
          del USER_STATE[chat_id]
        welcome_msg = "أهلاً بك مرة أخرى في القائمة الرئيسية للمتجر 🎮🔥"
        keyboard = {
            "inline_keyboard": [
                [{"text": "🛒 تصفح باقات الشدات", "callback_data": "fetch_live_data"}],
                [{"text": "📞 التواصل والدعم", "callback_data": "support"}]
            ]
        }
        edit_telegram_message(chat_id, message_id, welcome_msg, keyboard)

      elif callback_data == "support":
        support_msg = (
            "للتواصل والدعم الفني عبر تليجرام:\n🆔 Account ID: 7383417915"
        )
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔙 رجوع", "callback_data": "main_menu"}]
            ]
        }
        edit_telegram_message(chat_id, message_id, support_msg, keyboard)

    return "OK", 200
  except Exception as e:
    logger.error(f"Webhook Execution Error: {e}")
    return "OK", 200


def setup_webhook():
  try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={RENDER_URL}/{BOT_TOKEN}"
    response = requests.get(url, timeout=10)
    logger.info(f"Set Webhook Response: {response.text}")
  except Exception as e:
    logger.error(f"Failed to set webhook: {e}")


if __name__ == "__main__":
  setup_webhook()
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port, use_reloader=False)
