import os
import requests
from flask import Flask, request

TELEGRAM_BOT_TOKEN = "9250643163:AAGdWbppH2M5YzPMNG5QOH_Hp3RVH29KDYo"
ONE_STORE_API_URL = "https://api.one1store.com"
ONE_STORE_TOKEN = "5cd3e0be65d5093b018b4f1f482e1266fae0b92f954f"

app_flask = Flask(__name__)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

@app_flask.route("/", methods=["GET"])
def index():
    return "Bot is running perfectly!", 200

@app_flask.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip()

            if text == "/start":
                send_telegram_message(chat_id, "أهلاً بك يا أسطورة في متجرك الرسمي للخدمات الرقمية 🎮🔥\n\nاختر من الأوامر بالأسفل لتصفح المنتجات:")
            
            elif text == "/products":
                headers = {
                    "Authorization": f"Bearer {ONE_STORE_TOKEN}",
                    "api-token": ONE_STORE_TOKEN,
                    "Accept": "application/json"
                }
                products_url = f"{ONE_STORE_API_URL}/client/api/products/"
                
                response = requests.get(products_url, headers=headers)
                
                if response.status_code == 200:
                    try:
                        res_data = response.json()
                        items = res_data.get('data', res_data) if isinstance(res_data, dict) else res_data
                        
                        if items:
                            products_text = "📦 **قائمة المنتجات المتاحة من متجرك:**\n\n"
                            for item in items[:15]:
                                name = item.get('name', 'منتج رقمي')
                                price = item.get('price', 'غير محدد')
                                prod_id = item.get('id', '')
                                products_text += f"🔹 {name}\n💰 السعر: {price}\n🆔 المعرف: `{prod_id}`\n\n"
                            send_telegram_message(chat_id, products_text)
                        else:
                            send_telegram_message(chat_id, "⚠️ تم الاتصال بنجاح، ولكن قائمة المنتجات فارغة حالياً.")
                    except Exception:
                        send_telegram_message(chat_id, "⚠️ حدث خطأ في معالجة بيانات المنتجات.")
                else:
                    send_telegram_message(chat_id, f"⚠️ خطأ بالمزود ({response.status_code}) - تأكد من تفعيل الـ API في لوحة تحكم المتجر.")
            else:
                send_telegram_message(chat_id, "أهلاً بك! أرسل الأمر /products لعرض المنتجات المتاحة.")
                
    except Exception as e:
        print(f"Error: {str(e)}")
        
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
