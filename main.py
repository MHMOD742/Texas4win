import os
import requests
from flask import Flask, request

# توكن بوتك ومعرفك الشخصي
TELEGRAM_BOT_TOKEN = "9250643163:AAGdWbppH2M5YzPMNG5QOH_Hp3RVH29KDYo"
ADMIN_TELEGRAM_ID = 7383417915

# ضع هنا رابط الـ API الصحيح المخصص لجلب المنتجات من مزودك (مثلاً نهاية الـ endpoint الخاصة بالمنتجات)
API_ENDPOINT_URL = "https://api.one1store.com/client/api/products"
API_TOKEN = "5cd3e0be65d5093b018b4f1f482e1266fae0b92f954f"

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
    return "API Connected Bot is running successfully!", 200

@app_flask.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            user_name = message["from"].get("first_name", "صديقي")
            text = message.get("text", "").strip()

            if text == "/start":
                send_telegram_message(
                    chat_id, 
                    f"أهلاً بك يا {user_name} في متجرك الرسمي 🎮🔥\n\nأرسل الأمر /products لجلب المنتجات الحقيقية مباشرة عبر الـ API:"
                )
            
            elif text == "/products":
                # إعدادات التوثيق والاتصال بالـ API الحقيقي
                headers = {
                    "Authorization": f"Bearer {API_TOKEN}",
                    "api-token": API_TOKEN,
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
                
                try:
                    # إجراء الاتصال وسحب البيانات
                    response = requests.get(API_ENDPOINT_URL, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        res_json = response.json()
                        # استخراج المنتجات بناءً على هيكلية الـ JSON المتوقعة
                        items = res_json.get('data', res_json.get('products', res_json))
                        
                        if items and isinstance(items, list):
                            products_text = "📦 **قائمة المنتجات المسحوبة عبر الـ API:**\n\n"
                            for item in items[:15]:
                                name = item.get('name', item.get('title', 'منتج رقمي'))
                                price = item.get('price', 'غير متوفر')
                                prod_id = item.get('id', '')
                                products_text += f"🔹 **{name}**\n💰 السعر: {price}\n🆔 المعرف: `{prod_id}`\n\n"
                            send_telegram_message(chat_id, products_text)
                        else:
                    # في حال كانت البيانات تأتي بنمط آخر
                            send_telegram_message(chat_id, f"✅ تم الاتصال بنجاح بالـ API، الاستجابة الواردة:\n`{str(res_json)[:500]}`")
                    else:
                        send_telegram_message(chat_id, f"⚠️ خطأ بالاتصال مع الـ API (رمز الاستجابة: {response.status_code}) - تأكد من صلاحيات الرابط والتوكن.")
                
                except Exception as api_err:
                    send_telegram_message(chat_id, f"⚠️ حدث استثناء أثناء جلب البيانات: {str(api_err)}")
            else:
                send_telegram_message(chat_id, "أهلاً بك! أرسل الأمر /products لجلب المنتجات.")
                
    except Exception as e:
        print(f"Error: {str(e)}")
        
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
