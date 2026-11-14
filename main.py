import logging
import os
from flask import Flask
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)
from telegram.request import HTTPXRequest

# إعدادات الـ Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "9257361616:AAFtR4Cq-9-3bPMIEoAVK5em-2HoYUSAuio"
ONE_STORE_API_URL = "https://one1store.com/api"
API_TOKEN = "6315cd3e0be65d5093b01b8a4f1f482e1266fae0b92f954f"

# خادم ويب لـ Render
app = Flask(__name__)


@app.route("/")
def home():
  return "One Store Telegram Bot is running perfectly!"


def fetch_from_one_store(endpoint):
  headers = {"Authorization": f"Bearer {API_TOKEN}", "Accept": "application/json"}
  try:
    url = f"{ONE_STORE_API_URL}/{endpoint}"
    response = requests.get(url, headers=headers, timeout=20)
    logger.info(f"API URL: {url} | Status: {response.status_code}")
    logger.info(f"API Response Body: {response.text}")
    return response.json()
  except Exception as e:
    logger.error(f"API Error on {endpoint}: {e}")
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_name = update.effective_user.first_name
  welcome_message = (
      f"أهلاً بك يا أسطورة {user_name} في متجر الشحن الرسمي عبر One Store 🎮🔥\n\n"
      "اختر من الأزرار بالأسفل لتصفح المنتجات والخدمات المتوفرة:"
  )

  keyboard = [
      [InlineKeyboardButton("🛒 تصفح المنتجات والأقسام", callback_data="fetch_live_data")],
      [InlineKeyboardButton("📞 التواصل والدعم", callback_data="support")],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  if update.message:
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
  elif update.callback_query:
    await update.callback_query.message.edit_text(
        welcome_message, reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  if query.data == "fetch_live_data":
    # جلب المنتجات مباشرة من One Store API
    data = fetch_from_one_store("products")
    if not data:
      data = fetch_from_one_store("categories")

    keyboard = []
    
    if data:
      items = []
      if isinstance(data, list):
        items = data
      elif isinstance(data, dict):
        for key in ["data", "products", "categories", "items", "result"]:
          if key in data and isinstance(data[key], list):
            items = data[key]
            break

      for item in items:
        if isinstance(item, dict):
          name = item.get("name", item.get("title", "منتج بدون اسم"))
          item_id = str(item.get("id", ""))
          keyboard.append([InlineKeyboardButton(f"📦 {name}", callback_data=f"item_{item_id}")])

    # إذا لم تصدر البيانات كقائمة نضع زر افتراضي للتأكيد
    if not keyboard:
      keyboard.append([InlineKeyboardButton("📦 باقة 60 شدة (UC)", callback_data="buy_60")])
      keyboard.append([InlineKeyboardButton("📦 باقة 325 شدة (UC)", callback_data="buy_325")])

    keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        "📂 قائمة المنتجات المتوفرة في متجرك:",
        reply_markup=reply_markup,
    )
  elif query.data == "main_menu":
    await start(update, context)
  elif query.data == "support":
    await query.message.edit_text(
        "للتواصل والدعم الفني عبر تليجرام:\n🆔 Account ID: 7383417915",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
        ),
    )


def main():
  request_settings = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
  application = (
      ApplicationBuilder().token(BOT_TOKEN).request(request_settings).build()
  )

  application.add_handler(CommandHandler("start", start))
  application.add_handler(CallbackQueryHandler(button_handler))

  logger.info("Starting bot polling cleanly...")
  # إجبار التليجرام على تجاهل أي تجمعات قديمة وبدء اتصال نظيف
  application.run_polling(
      drop_pending_updates=True,
      allowed_updates=Update.ALL_TYPES,
      stop_signals=None,
  )


if __name__ == "__main__":
  import threading

  def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

  web_thread = threading.Thread(target=run_web)
  web_thread.daemon = True
  web_thread.start()

  main()
