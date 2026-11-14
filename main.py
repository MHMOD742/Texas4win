import logging
import os
import requests
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

# إعدادات الـ Logging لمتابعة عمل البوت
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# التوكن الصحيح الخاص بك
BOT_TOKEN = "9257361616:AAFtR4Cq-9-3bPMIEoAVK5em-2HoYUSAuio"
ONE_STORE_API_URL = "https://one1store.com/api"

# إنشاء تطبيق ويب وهمي لإرضاء الاستضافة
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is active and running 24/7!"


# أمر البداية /start
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


# معالجة الضغط على الأزرار
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

  elif query.data == "services_menu":
    keyboard = [
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(
        "قسم الخدمات الأخرى قيد التحديث قريباً..", reply_markup=reply_markup
    )

  elif query.data == "support":
    keyboard = [
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(
        "للدعم الفني والاستفسارات، تواصل عبر حساب المالك الرسمي.",
        reply_markup=reply_markup,
    )

  elif query.data == "main_menu":
    await start(update, context)

  elif query.data.startswith("buy_"):
    await query.message.edit_text(
        "تم استلام طلبك بنجاح! الرجاء إرسال الآيدي (Player ID) الخاص بك للمتابعة:"
    )


# استقبال الرسائل النصية
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text = update.message.text
  await update.message.reply_text(
      f"تم استلام النص: ({text}). جاري معالجة الطلب عبر One Store..."
  )


def run_telegram_bot():
  request_settings = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
  application = (
      ApplicationBuilder().token(BOT_TOKEN).request(request_settings).build()
  )

  application.add_handler(CommandHandler("start", start))
  application.add_handler(CallbackQueryHandler(button_handler))
  application.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
  )

  logger.info("Telegram Bot is running via polling...")
  application.run_polling()


if __name__ == "__main__":
  import threading

  bot_thread = threading.Thread(target=run_telegram_bot)
  bot_thread.daemon = True
  bot_thread.start()

  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
