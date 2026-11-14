import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# تفعيل نظام سجلات الأخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توكن البوت الخاص بك
BOT_TOKEN = "ضع_توكن_بوتك_هنا"

# مفتاح API الخاص بحسابك على موقع One Store الذي قمت بنسخه
ONE_STORE_API_TOKEN = "5cd3e0be65d093b01b8a4f1f482e1266fae0b92f954f"
ONE_STORE_API_URL = "https://one1store.com/api"

# دالة أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 متجر البطاقات الرقمية", callback_data='shop')],
        [InlineKeyboardButton("👤 معلومات الملف الشخصي", callback_data='profile')],
        [InlineKeyboardButton("📥 شحن البوت", callback_data='deposit')],
        [InlineKeyboardButton("📞 تواصل مع الدعم الفني", callback_data='support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "✨ أهلاً بك! اختر الخدمة المطلوبة من الأزرار أدناه:",
        reply_markup=reply_markup
    )

# دالة التعامل مع الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'shop':
        await query.message.reply_text("🛍️ متجر البطاقات الرقمية قيد التفعيل والربط الآلي مع One Store.")
    elif query.data == 'profile':
        await query.message.reply_text(f"👤 معلومات الحساب مرتبطة بنجاح مع One Store باستخدام مفتاح الـ API المفعل.")
    elif query.data == 'deposit':
        await query.message.reply_text("💳 لشحن رصيدك عبر شام كاش، يرجى التواصل مع الإدارة أو الوكيل المعتمد.")
    elif query.data == 'support':
        await query.message.reply_text("📞 للتواصل مع الدعم الفني، يرجى إرسال رسالتك هنا وستم الرد عليك قريباً.")

# التعامل مع الرسائل النصية
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("✅ تم استلام رسالتك. سيتم معالجة الطلب عبر النظام الآلي قريباً.")

# تشغيل البوت
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
