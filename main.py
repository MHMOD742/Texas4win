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

def send_order_to_one_store(product_id, player_id):
  """دالة لتجربة إرسال الطلب أوتوماتيكياً عبر POST API للموقع"""
  headers = {
      "Authorization": f"Bearer {API_TOKEN}",
      "Accept": "application/json",
      "Content-Type": "application/json"
  }
  
  # بيانات الطلب التجريبية المحتملة
  payload = {
      "product_id": product_id,
      "player_id": player_id,
      "quantity": 1
  }
  
  # مسارات إنشاء الطلبات المحتملة في لوحات المتاجر
  endpoints = [
      "api/v1/orders",
      "api/orders",
      "api/order",
      "api/v1/order/store",
      "orders"
  ]
  
  for endpoint in endpoints:
    url = f"{ONE_STORE_API_URL}/{endpoint}"
    try:
      logger.info(f"Trying POST Order URL: {url} with payload {payload}")
      response = requests.post(url, json=payload, headers=headers, timeout=15)
      logger.info(f"POST Response Status: {response.status_code}")
      logger.info(f"POST Response Text: {response.text[:300]}")
      
      if response.status_code in [200, 201]:
        logger.info(f"Successfully placed order via {endpoint}!")
        return True
    except Exception as e:
      logger.error(f"Error posting order to {endpoint}: {e}")
      
  return False

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
  return "One Store Automation Bot is running!"

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
            f"أهلاً بك يا أسطورة *{user_name}* في متجر الشحن الرسمي 🎮🔥\n\n"
            "اختر باقتك المطلوبة لبدء الطلب الآلي:"
        )
        keyboard = {
            "inline_keyboard": [
                [{"text": "📦 باقة 60 شدة (UC) - 143,899 ليرة", "callback_data": "prod_60_143899"}],
                [{"text": "📦 باقة 325 شدة (UC) - 700,000 ليرة", "callback_data": "prod_325_700000"}]
            ]
        }
        send_telegram_message(chat_id, welcome_msg, keyboard)

      elif chat_id in USER_STATE:
        state_data = USER_STATE[chat_id]
        product_id = state_data["product_id"]
        product_name = state_data["product_name"]
        player_id = text.strip()

        del USER_STATE[chat_id]

        # محاولة إرسال الطلب أوتوماتيكياً للموقع
        api_success = send_order_to_one_store(product_id, player_id)

        if api_success:
          confirmation_msg = (
              f"✅ *تم إرسال طلبك وتنفيذه أوتوماتيكياً عبر النظام!* 🚀\n\n"
              f"📦 المنتج: *{product_name}*\n"
              f"🆔 آيدي اللاعب: `{player_id}`\n\n"
              "تم شحن حسابك بنجاح!"
          )
        else:
          confirmation_msg = (
              f"✅ *تم استلام طلبك بنجاح يا أسطورة!*\n\n"
              f"📦 المنتج: *{product_name}*\n"
              f"🆔 آيدي اللاعب: `{player_id}`\n\n"
              "يرجى تحويل المبلغ عبر (شام كاش) وإرسال الإيصال للتنفيذ الفوري!"
          )
        
        send_telegram_message(chat_id, confirmation_msg)

        admin_notification = (
            f"🚨 *طلب شراء جديد في البوت!* 🚨\n\n"
            f"👤 الزبون: {user_name} (`{chat_id}`)\n"
            f"📦 المنتج: *{product_name}*\n"
            f"🆔 الآيدي: `{player_id}`\n"
            f"⚙️ حالة الأتمتة: {'تم إرساله للموقع أوتوماتيكياً' if api_success else 'يحتاج تنفيذ يدوي'}"
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

      if callback_data.startswith("prod_"):
        parts = callback_data.split("_")
        prod_id = parts[1]
        raw_price = parts[2]
        
        product_name = f"باقة {prod_id} شدة (UC)"
        formatted_price = f"{int(raw_price):,} ليرة سورية"

        USER_STATE[chat_id] = {
            "product_id": prod_id,
            "product_name": product_name
        }

        prompt_msg = (
            f"لقد اخترت: *{product_name}* - *{formatted_price}*\n\n"
            "👇 **الرجاء إرسال آيدي اللعبة (Player ID) في الدردشة الآن:**"
        )
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔙 إلغاء والعودة", "callback_data": "cancel"}]
            ]
        }
        edit_telegram_message(chat_id, message_id, prompt_msg, keyboard)

      elif callback_data == "cancel":
        if chat_id in USER_STATE:
          del USER_STATE[chat_id]
        welcome_msg = "تم الإلغاء. أهلاً بك في القائمة الرئيسية 🎮🔥"
        keyboard = {
            "inline_keyboard": [
                [{"text": "📦 باقة 60 شدة (UC) - 143,899 ليرة", "callback_data": "prod_60_143899"}],
                [{"text": "📦 باقة 325 شدة (UC) - 700,000 ليرة", "callback_data": "prod_325_700000"}]
            ]
        }
        edit_telegram_message(chat_id, message_id, welcome_msg, keyboard)

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
  port = int(os.environ.0.get("PORT", 10000) if hasattr(os.environ, 'get') else 10000)
  app.run(host="0.0.0.0", port=port, use_reloader=False)
