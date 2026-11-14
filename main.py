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
    MessageHandler,
    filters,
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

# خادم ويب خفيف لـ Render
app = Flask(__name__)


@app.route("/")
def home():
  return "One Store Telegram Bot is running!"


def fetch_from_one_store(endpoint, payload=None):
  headers = {"Authorization": f"Bearer {API_TOKEN}", "Accept": "application/json"}
  try:
    url = f"{ONE_STORE_API_URL}/{endpoint}"
    if payload:
      response = requests.post(url, json=payload, headers=headers, timeout=20)
    else:
      response = requests.get(url, headers=headers, timeout=20)
    return response.json()
  except Exception as e:
    logger.error(f"API Error: {e}")
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_name = update.effective_user.first_name
  welcome_message = (
      f"أهلاً بك يا أسطورة {user_name} في متجر الشحن الرسمي عبر One Store 🎮🔥\n\n"
      "اختر من الأزرار بالأسفل لتصفح الخدمات والأقسام المتوفرة:"
  )

  keyboard = [
      [InlineKeyboardButton("🛒 تصفح أقسام المتجر", callback_data="fetch_categories")],
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

  if query.data == "fetch_categories":
    # جلب الأقسام أو المنتجات من One Store API
    # (يمكنك تعديل الـ endpoint حسب مسار الـ API المعتمد لديك)
    data = fetch_from_one_store("categories")  # أو المنتجات

    keyboard = []
    # مثال تفاعلي في حال جلب البيانات بنجاح أو عرض زر رجوع
    keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        "📦 جاري جلب الأقسام والخدمات المتوفرة في حسابك على One Store...",
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

  logger.info("Starting bot polling with One Store API integration...")
  application.run_polling(drop_pending_updates=True, stop_signals=None)


if __name__ == "__main__":
  import threading

  def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

  web_thread = threading.Thread(target=run_web)
  web_thread.daemon = True
  web_thread.start()

  main()
