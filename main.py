import logging
import os
from flask import Flask
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

# خادم ويب خفيف جداً لـ Render فقط بدون تعقيد الـ Threads
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is running!"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_name = update.effective_user.first_name
  welcome_message = (
      f"أهلاً بك يا أسطورة {user_name} في متجر الشحن الرسمي 🎮🔥\n\n"
      "اختر القسم المناسب لك من الأزرار بالأسفل لشحن شداتك وخدماتك فوراً:"
  )

  keyboard = [
      [InlineKeyboardButton("🛒 شحن شدات PUBG Mobile", callback_data="pubg_menu")],
      [InlineKeyboardButton("💳 رصيد وخدمات أخرى", callback_data="services_menu")],
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

  if query.data == "pubg_menu":
    keyboard = [
        [InlineKeyboardButton("60 شدة (UC)", callback_data="buy_60_uc")],
        [InlineKeyboardButton("325 شدة (UC)", callback_data="buy_325_uc")],
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(
        "اختر باقة الشدات المطلوبة:", reply_markup=reply_markup
    )
  elif query.data == "main_menu":
    await start(update, context)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text = update.message.text
  await update.message.reply_text(
      f"تم استلام النص: ({text}). جاري المعالجة عبر One Store..."
  )


def main():
  request_settings = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
  application = (
      ApplicationBuilder().token(BOT_TOKEN).request(request_settings).build()
  )

  application.add_handler(CommandHandler("start", start))
  application.add_handler(CallbackQueryHandler(button_handler))
  application.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
  )

  logger.info("Starting bot polling...")
  # تشغيل البوت بالطريقة النظامية المباشرة مع إيقاف فحص الـ signals لتجنب خطأ الثريد
  application.run_polling(drop_pending_updates=True, stop_signals=None)


if __name__ == "__main__":
  # لتشغيل Flask و البوت معاً بدون مشاكل، سنجعل المنصة تشغل البوت مباشرة
  # أو نقوم بتشغيل سيرفر الويب في الخلفية بشكل آمن:
  import threading

  def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

  web_thread = threading.Thread(target=run_web)
  web_thread.daemon = True
  web_thread.start()

  # تشغيل البوت في المجلد الرئيسي لتفادي خطأ الـ Interpreter
  main()
