import os
import requests
from flask import Flask, request

# توكن بوتك ومعرفك الشخصي
TELEGRAM_BOT_TOKEN = "9250643163:AAGdWbppH2M5YzPMNG5QOH_Hp3RVH29KDYo"
ADMIN_TELEGRAM_ID = 7383417915

# إعدادات One Store API الحقيقية
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
    return "Bot is running and connected to One Store API!", 200

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
                    f"أهلاً بك يا {user_name} في متجرك الرسمي للخدمات الرقمية 🎮🔥\n\nأرسل الأمر /products لعرض المنتجات الحقيقية المتاحة من متجرك."
                )
            
            elif text == "/products":
                # الترويسة القياسية المعتمدة لسحب المنتجات الحقيقية
                headers = {
                    "Authorization": f"Bearer {ONE_STORE_TOKEN}",
                    "api-token": ONE_STORE_TOKEN,
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
                products_url = f"{ONE_STORE_API_URL}/client/api/products/"
                
                try:
                    response = requests.get(products_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        items = res_data.get('data', res_data) if isinstance(res_data, dict) else res_data
                        
                        if items:
                            products_text = "📦 **قائمة منتجاتك الحقيقية (One Store):**\n\n"
                            for item in items[:15]:
                                name = item.get('name', 'منتج رقمي')
                                price = item.get('price', 'غير محدد')
                                prod_id = item.get('id', '')
                                products_text += f"🔹 {name}\n💰 السعر: {price}\n🆔 المعرف: `{prod_id}`\n\n"
                            send_telegram_message(chat_id, products_text)
                        else:
                            send_telegram_message(chat_id, "⚠️ تم الاتصال بنجاح، ولكن قائمة المنتجات في حسابك فارغة حالياً.")
                    else:
                        send_telegram_message(chat_id, f"⚠️ خطأ بالمزود ({response.status_code}) - تأكد من صلاحيات التوكن في لوحة تحكم One Store.")
                except Exception as api_err:
                    send_telegram_message(chat_id, f"⚠️ حدث خطأ أثناء الاتصال بالمزود: {str(api_err)}")
            else:
                send_telegram_message(chat_id, "أهلاً بك! أرسل الأمر /products لعرض منتجات متجرك الحقيقية.")
                
    except Exception as e:
        print(f"Error: {str(e)}")
        
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
