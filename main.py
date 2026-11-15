import os
import requests
from flask import Flask, request
from telegram import Update, Bot

# إعدادات التوكن والبيانات الأساسية
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "9257361616:AAFtR4Cq-9-3bPMIEoAVK5em-2HoYUSAuio")
NIMER_API_URL = "https://nemer-card.com"
NIMER_API_TOKEN = "WVJccdFfXYncjTbCXbEQmyPxwK32KIVTaOXS"

app_flask = Flask(__name__)
bot = Bot(token=TOKEN)

@app_flask.route("/", methods=["GET"])
def index():
    return "Bot is running successfully with Nimer Card API!", 200

@app_flask.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """استقبال التحديثات والرسائل من تيليجرام ومعالجتها"""
    if request.method == "POST":
        try:
            json_data = request.get_json(force=True)
            message = json_data.get("message", {})
            text = message.get("text", "")
            chat_id = message.get("chat", {}).get("id")

            if text == "/products" and chat_id:
                # سحب المنتجات من نمر كارد عند طلب الأمر
                headers = {"api-token": NIMER_API_TOKEN}
                url = f"{NIMER_API_URL}/client/api/products/"
                
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('data', data) if isinstance(data, dict) else data
                    
                    products_text = "📦 **قائمة المنتجات المتاحة من نمر كارد:**\n\n"
                    for item in items[:10]:
                        name = item.get('name', 'منتج رقمي')
                        price = item.get('price', 'غير محدد')
                        prod_id = item.get('id', '')
                        products_text += f"🔹 {name}\n💰 السعر: {price}\n🆔 المعرف: `{prod_id}`\n\n"
                    
                    bot.send_message(chat_id=chat_id, text=products_text, parse_mode="Markdown")
                else:
                    bot.send_message(chat_id=chat_id, text="⚠️ تعذر سحب المنتجات من المزود حالياً.")
            
            elif chat_id:
                bot.send_message(chat_id=chat_id, text="أهلاً بك يا أسطورة! أرسل الأمر /products لعرض المنتجات المتاحة.")

        except Exception as e:
            print(f"Error handling update: {str(e)}")
            
        return "OK", 200
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app_flask.run(host="0.0.0.0", port=port)
