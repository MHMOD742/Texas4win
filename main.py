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
# استخدام الرابط المعتمد مع التوكن الخاص بحسابك
ONE_STORE_API_URL = "https://one1store.com/api"
API_TOKEN = "6315cd3e0be65d5093b01b8a4f1f482e1266fae0b92f954f"
RENDER_URL = "https://texas4win-1.onrender.com"

app = Flask(__name__)


def fetch_from_one_store(endpoint):
  headers = {
      "Authorization": f"Bearer {API_TOKEN}",
      "Accept": "application/json",
      "User-Agent": "Mozilla/5.0",
  }
  try:
    url = f"{ONE_STORE_API_URL}/{endpoint}"
    response = requests.get(url, headers=headers, timeout=20)
    logger.info(f"=== API REQUEST: {url} | Status: {response.status_code} ===")
    
    if response.status_code == 200:
      try:
        return response.json()
      except Exception:
        logger.error(f"Response is not JSON: {response.text[:200]}")
        return None
    else:
      logger.error(f"API Error Response: {response.text[:200]}")
      return None
  except Exception as e:
    logger.error(f"API Connection Exception on {endpoint}: {e}")
    return None


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
  return "One Store Telegram Bot is running perfectly!"


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
        welcome_msg = (
            f"أهلاً بك يا أسطورة {user_name} في متجر الشحن الرسمي عبر One Store 🎮🔥\n\n"
            "اختر من الأزرار بالأسفل لتصفح جميع منتجات وأقسام متجرك الحقيقية:"
        )
        keyboard = {
            "inline_keyboard": [
                [{"text": "🛒 تصفح جميع منتجات المتجر", "callback_data": "fetch_live_data"}],
                [{"text": "📞 التواصل والدعم", "callback_data": "support"}]
            ]
        }
        send_telegram_message(chat_id, welcome_msg, keyboard)

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
        # محاولة سحب المنتجات من مسارات النظام المختلفة
        api_data = fetch_from_one_store("products")
        if not api_data:
          api_data = fetch_from_one_store("items")
        if not api_data:
          api_data = fetch_from_one_store("categories")

        inline_keyboard = []
        
        if api_data:
          items = []
          if isinstance(api_data, list):
            items = api_data
          elif isinstance(api_data, dict):
            for key in ["data", "products", "items", "categories", "result"]:
              if key in api_data and isinstance(api_data[key], list):
                items = api_data[key]
                break

          for item in items:
            if isinstance(item, dict):
              name = item.get("name", item.get("title", "منتج بدون اسم"))
              item_id = str(item.get("id", ""))
              inline_keyboard.append([{"text": f"📦 {name}", "callback_data": f"item_{item_id}"}])

        if not inline_keyboard:
          # باقات افتراضية مؤقتة في حال لم يتم جلب البيانات لتفادي فراغ القائمة
          inline_keyboard.append([{"text": "📦 باقة 60 شدة (UC)", "callback_data": "buy_60"}])
          inline_keyboard.append([{"text": "📦 باقة 325 شدة (UC)", "callback_data": "buy_325"}])

        inline_keyboard.append([{"text": "🔙 رجوع للقائمة الرئيسية", "callback_data": "main_menu"}])
        
        edit_telegram_message(
            chat_id,
            message_id,
            "📂 جميع المنتجات المتوفرة في حسابك على One Store:",
            {"inline_keyboard": inline_keyboard}
        )

      elif callback_data == "main_menu":
        welcome_msg = "أهلاً بك مرة أخرى في القائمة الرئيسية للمتجر 🎮🔥"
        keyboard = {
            "inline_keyboard": [
                [{"text": "🛒 تصفح جميع منتجات المتجر", "callback_data": "fetch_live_data"}],
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
