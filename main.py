import logging
import os
from flask import Flask, request as flask_request
import requests

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "9257361616:AAFtR4Cq-9-3bPMIEoAVK5em-2HoYUSAuio"
RENDER_URL = "https://texas4win-1.onrender.com"
ADMIN_TELEGRAM_ID = "7383417915"

ONE_STORE_API_URL = "https://api.one1store.com"
API_TOKEN = "6315cd3e0be65d5093b01b8a4f1f482e1266fae0b92f954f"

app = Flask(__name__)
USER_STATE = {}

def fetch_products_from_one_store():
  headers = {
      "Authorization": f"Bearer {API_TOKEN}",
      "Accept": "application/json",
      "Content-Type": "application/json"
  }
  
  # مسارات دقيقة ومحدثة لتجنب خطأ 404
  endpoints = [
      "api/v1/products",
      "api/store/products",
      "api/user/products",
      "api/v1/services",
      "api/items",
      "v1/products"
  ]
  
  for endpoint in endpoints:
    url = f"{ONE_STORE_API_URL}/{endpoint}"
    try:
      logger.info(f"Trying API URL: {url}")
      response = requests.get(url, headers=headers, timeout=15)
      logger.info(f"Response Status: {response.status_code}")
      logger.info(f"Response Text: {response.text[:300]}")
      
      if response.status_code == 200:
        data = response.json()
        items = []
        if isinstance(data, list):
          items = data
        elif isinstance(data, dict):
          for key in ["data", "products", "items", "result", "list"]:
            if key in data and isinstance(data[key], list):
              items = data[key]
              break
        
        if items:
          logger.info(f"Successfully fetched {len(items)} products from {endpoint}")
          return items
    except Exception as e:
      logger.error(f"Error fetching from {endpoint}: {e}")
      
  return None

def send_telegram_message(chat_id, text, reply_markup=None):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
  if reply_markup:
    payload["reply_markup"] = reply_markup
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    logger.error(f"TG Send Error: {e}")

def edit_telegram_message(chat_id, message_id, text, reply_markup=None):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
  payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "Markdown"}
  if reply_markup:
    payload["reply_markup"] = reply_markup
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    logger.error(f"TG Edit Error: {e}")

@app.route("/")
def home():
  return "One Store Live API Bot is running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
  try:
    data = flask_request.get_json(force=True)
    
    if "message" in data:
      msg = data["message"]
      chat_id = msg["chat"]["id"]
      user_name = msg.get("from", {}).get("first_name", "صديقي")
      text = msg.get("text", "")

      if text.startswith("/start"):
        if chat_id in USER_STATE:
          del USER_STATE[chat_id]

        welcome_msg = (
            f"أهلاً بك يا أسطورة {user_name} في متجر الشحن الرسمي 🎮🔥\n\n"
            "اختر من الأزرار بالأسفل لتصفح المنتجات الحية من متجرك:"
        )
        keyboard = {
            "inline_keyboard": [
                [{"text": "🛒 تصفح المنتجات الحية", "callback_data": "fetch_live_products"}],
                [{"text": "📞 التواصل والدعم", "callback_data": "support"}]
            ]
        }
        send_telegram_message(chat_id, welcome_msg, keyboard)

      elif chat_id in USER_STATE:
        state_data = USER_STATE[chat_id]
        product_name = state_data["product_name"]
        player_id = text.strip()

        del USER_STATE[chat_id]

        confirmation_msg = (
            f"✅ تم استلام طلبك بنجاح يا أسطورة!\n\n"
            f"📦 المنتج: *{product_name}*\n"
            f"🆔 آيدي اللاعب: `{player_id}`\n\n"
            "يرجى تحويل المبلغ عبر (شام كاش) وإرسال صورة الإيصال هنا للتنفيذ الفوري!"
        )
        send_telegram_message(chat_id, confirmation_msg)

        admin_notification = (
            f"🚨 *طلب شراء جديد من البوت!* 🚨\n\n"
            f"👤 اسم المستخدم: {user_name}\n"
            f"💬 معرف المستخدم: `{chat_id}`\n"
            f"📦 المنتج: *{product_name}*\n"
            f"🆔 آيدي اللاعب: `{player_id}`"
        )
        send_telegram_message(ADMIN_TELEGRAM_ID, admin_notification)

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

      if callback_data == "fetch_live_products":
        api_items = fetch_products_from_one_store()
        inline_keyboard = []

        if api_items:
          for item in api_items:
            name = item.get("name", item.get("title", "منتج"))
            price = item.get("price", "")
            item_id = str(item.get("id", ""))
            button_text = f"📦 {name}" + (f" - {price}" if price else "")
            inline_keyboard.append([{"text": button_text, "callback_data": f"prod_{item_id}"}])
        
        if not inline_keyboard:
          inline_keyboard.append([{"text": "📦 باقة 60 شدة (UC) - 143,899 ليرة", "callback_data": "prod_60"}])
          inline_keyboard.append([{"text": "📦 باقة 325 شدة (UC) - 700,000 ليرة", "callback_data": "prod_325"}])

        inline_keyboard.append([{"text": "🔙 رجوع للقائمة الرئيسية", "callback_data": "main_menu"}])

        edit_telegram_message(
            chat_id,
            message_id,
            "📂 قائمة المنتجات المتاحة:",
            {"inline_keyboard": inline_keyboard}
        )

      elif callback_data.startswith("prod_"):
        product_id = callback_data.replace("prod_", "")
        
        product_name = f"منتج رقم {product_id}"
        if product_id == "60":
          product_name = "باقة 60 شدة (UC)"
        elif product_id == "325":
          product_name = "باقة 325 شدة (UC)"

        USER_STATE[chat_id] = {"product_name": product_name}

        prompt_msg = (
            f"لقد اخترت: *{product_name}*\n\n"
            "👇 **الرجاء إرسال الآيدي (Player ID) الخاص بك في اللعبة الآن بالدردشة:**"
        )
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔙 عودة لقائمة المنتجات", "callback_data": "fetch_live_products"}],
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
                [{"text": "🛒 تصفح المنتجات الحية", "callback_data": "fetch_live_products"}],
                [{"text": "📞 التواصل والدعم", "callback_data": "support"}]
            ]
        }
        edit_telegram_message(chat_id, message_id, welcome_msg, keyboard)

      elif callback_data == "support":
        support_msg = "للتواصل والدعم الفني:\n🆔 Account ID: 7383417915"
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔙 رجوع", "callback_data": "main_menu"}]
            ]
        }
        edit_telegram_message(chat_id, message_id, support_msg, keyboard)

    return "OK", 200
  except Exception as e:
    logger.error(f"Webhook Error: {e}")
    return "OK", 200

def setup_webhook():
  try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={RENDER_URL}/{BOT_TOKEN}"
    requests.get(url, timeout=10)
  except Exception as e:
    logger.error(f"Webhook setup error: {e}")

if __name__ == "__main__":
  setup_webhook()
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port, use_reloader=False)
