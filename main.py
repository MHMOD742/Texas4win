import os
import requests
from flask import Flask, request

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "9257361616:AAFtR4Cq-9-3bPMIEoAVK5em-2HoYUSAuio")
NIMER_API_URL = "https://nemer-card.com"
NIMER_API_TOKEN = "WVJccdFfXYncjTbCXbEQmyPxwK32KIVTaOXS"

app_flask = Flask(__name__)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

@app_flask.route("/", methods=["GET"])
def index():
    return "Bot is running perfectly!", 200

@app_flask.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip()

            if text == "/products" or text == "/test":
                # إرسال التوكن بعدة طرق في نفس الوقت لضمان قبول المزود له
                headers = {
                    "api-token": NIMER_API_TOKEN,
                    "Authorization": f"Bearer {NIMER_API_TOKEN}",
                    "Accept": "application/json"
                }
                
                # تجربة الرابط مع تمرير التوكن هيدر وفي الرابط إن لم ينجح
                products_url = f"{NIMER_API_URL}/client/api/products/"
                
                response = requests.get(products_url, headers=headers)
                print(f"Status Code: {response.status_code}")
                print(f"Response Text: {response.text}")
                
                if response.status_code == 200:
                    try:
                        res_data = response.json()
                        items = res_data.get('data', res_data) if isinstance(res_data, dict) else res_data
                        
                        if items:
                            products_text = "📦 **قائمة المنتجات المتاحة من نمر كارد:**\n\n"
                            for item in items[:10]:
                                name = item.get('name', 'منتج رقمي')
                                price = item.get('price', 'غير محدد')
                                prod_id = item.get('id', '')
                                products_text += f"🔹 {name}\n💰 السعر: {price}\n🆔 المعرف: `{prod_id}`\n\n"
                            send_telegram_message(chat_id, products_text)
                        else:
                            send_telegram_message(chat_id, "⚠️ تم الاتصال بنجاح، ولكن القائمة فارغة حالياً.")
                    except Exception as parse_err:
                        send_telegram_message(chat_id, f"⚠️ رد المزود غير صالح: {str(parse_err)}")
                else:
                    send_telegram_message(chat_id, f"⚠️ خطأ في الاتصال بالمزود (رمز الاستجابة: {response.status_code})")
            else:
                send_telegram_message(chat_id, "أهلاً بك يا أسطورة! أرسل الأمر /products لجلب المنتجات من نمر كارد.")
                
    except Exception as e:
        print(f"Error: {str(e)}")
        
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
