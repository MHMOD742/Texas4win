import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# إعدادات التسجيل لمتابعة الأخطاء والعمليات
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# بيانات البوت والمنصة
BOT_TOKEN = "9257361616:AAFtR4Cq-9-3bPMIEoAVK5em-2HoYUSAuio"
ADMIN_ID = 7383417915  # آيدي الأدمن
SHAM_CASH_WALLET = "839875cca2341bad76e1ffe721d13788"
TEXAS_LINK = "https://texas4win200.com/"
CHANNEL_USERNAME = "@CAesar_Texas_Official"


# أمر البداية /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = update.effective_user
  keyboard = [
    [InlineKeyboardButton("🎮 الدخول لمنصة تكساس", url=TEXAS_LINK)],
    [InlineKeyboardButton("📢 قناة القيصر الرسمية", url=f"https://t.me/CAesar_Texas_Official")],
    [InlineKeyboardButton("💰 شحن الرصيد / شام كاش", callback_data="deposit_info")],
    [InlineKeyboardButton("🛠️ الخدمات والوكالة", callback_data="agency_info")],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  welcome_message = (
      f"أهلاً بك يا *{user.first_name}* في بوت الخدمات الرسمي (القيصر / تكساس) 🚀\n\n"
      "نحن وكلاء معتمدون لمنصة تكساس للألعاب. نوفر لك:\n"
      "• إنشاء حسابات سريعة وتلقائية.\n"
      "• شحن وسحب آمن عبر محفظة شام كاش.\n"
      "• دعم فني واستجابة فورية 24/7.\n\n"
      "اختر ما يناسبك من الأزرار أدناه للبدء:"
  )

  await update.message.reply_text(
      welcome_message, reply_markup=reply_markup, parse_mode="Markdown"
  )


# معالجة الأزرار التفاعلية
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  if query.data == "deposit_info":
    deposit_text = (
        "💳 *تعليمات الشحن والإيداع عبر شام كاش:*\n\n"
        "لإتمام عملية الشحن، يرجى التحويل إلى محفظة شام كاش الرسمية التالية:\n"
        f"`{SHAM_CASH_WALLET}`\n\n"
        "بعد إتمام التحويل، قم بإرسال صورة الإيصال أو رقم العملية هنا للبوت أو للمشرف ليتم إضافته لحسابك فوراً."
    )
    await query.edit_message_text(
        text=deposit_text, parse_mode="Markdown"
    )

  elif query.data == "agency_info":
    agency_text = (
        "🌟 *مميزات العمل معنا كوكيل رسمي:*\n\n"
        "• عمولات وأرباح ممتازة وتنافسية.\n"
        "• سرعة فائقة في معالجة طلبات السحب والإيداع.\n"
        "• دعم فني خاص ومتابعة مستمرة.\n\n"
        f"للاشتراك أو الاستفسار تواصل مباشرة مع الإدارة عبر القناة: {CHANNEL_USERNAME}"
    )
    await query.edit_message_text(text=agency_text, parse_mode="Markdown")


# استقبال الرسائل العامة وتنبيه الأدمن
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = update.effective_user
  text = update.message.text

  # إرسال تنبيه للإدمن في حال أرسل المستخدم رسالة أو طلب شحن
  notification = (
      f"📩 رسالة جديدة من المستخدم:\n"
      f"الاسم: {user.first_name} (ID: `{user.id}`)\n"
      f"النص: {text}"
  )

  try:
    await context.bot.send_message(
        chat_id=ADMIN_ID, text=notification, parse_mode="Markdown"
    )
  except Exception as e:
    logger.error(f"Failed to notify admin: {e}")

  await update.message.reply_text(
      "✅ تم استلام رسالتك بنجاح، سيتم الرد عليك ومراجعة طلبك في أقرب وقت ممكن من قبل الإدارة."
  )


# تشغيل البوت
def main():
  app = ApplicationBuilder().token(BOT_TOKEN).build()

  app.add_handler(CommandHandler("start", start))
  app.add_handler(CallbackQueryHandler(button_handler))
  app.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
  )

  print("Bot is running...")
  app.run_polling()


if __name__ == "__main__":
  main()
