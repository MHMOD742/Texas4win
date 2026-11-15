import os
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# بيانات الإعداد والتوصيل مع نمر كارد وتليجرام
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "حط_توكن_البوت_هنا")
NIMER_API_URL = "https://nemer-card.com"
NIMER_API_TOKEN = "WVJccdFfXYncjTbCXbEQmyPxwK32KIVTaOXS"  # التوكن الخاص بك[span_2](start_span)[span_2](end_span)

app_flask = Flask(__name__)
bot = Bot(token=TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة البداية للترحيب بالزبون"""
    await update.message.reply_text(
        "أهلاً بك يا أسطورة في متجرنا الرقمي! 🎮🔥\n"
        "للهيمنة وشحن شداتك أوتوماتيكياً، استخدم الأمر /products لعرض المنتجات المتاحة حالياً من المزود."
    )

async def get_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر لسحب وعرض المنتجات مباشرة من نمر كارد"""
    headers = {
        "api-token": NIMER_API_TOKEN
    }
    url = f"{NIMER_API_URL}/client/api/products/"
    
    try:
        # إرسال طلب GET لسحب المنتجات حسب التوثيق[span_3](start_span)[span_3](end_span)
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if response.status_code == 200 and data:
            products_text = "📦 **قائمة المنتجات المتاحة حالياً:**\n\n"
            # افتراض أن المنتجات تأتي على شكل قائمة
            items = data.get('data', data) if isinstance(data, dict) else data
            
            for item in items[:10]:  # عرض أول 10 منتجات كبداية
                name = item.get('name', 'منتج رقمي')
                price = item.get('price', 'غير محدد')
                product_id = item.get('id', '')
                products_text += f"🔹 **{name}**\n💰 السعر: {price}\n🆔 المعرف: `{product_id}`\n\n"
            
            await update.message.reply_text(products_text, parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ عذراً، لم يتم العثور على منتجات متاحة حالياً أو هناك خطأ في الاستعلام.")
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء الاتصال بالمزود: {str(e)}")

@app_flask.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """استقبال التحديثات من تيليجرام"""
    json_str = request.get_data().astype(str) if hasattr(request.get_data(), 'astype') else request.get_data().decode('utf-8')
    update = Update.de_json(requests.compat.json.loads(json_str), bot)
    # ملاحظة: يمكن ربط المعالجات هنا أو عبر Application
    return "OK", 200

@app_flask.route("/")
def index():
    return "Bot is running successfully!", 200

if __name__ == "__main__":
    # تشغيل سيرفر Flask على المنفذ المطلوب لـ Render
    port = int(os.environ.get("PORT", 5000))
    app_flask.run(host="0.0.0.0", port=port)
