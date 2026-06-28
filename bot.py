import os
import threading
import http.server
import socketserver
import telebot
import requests

# --- سيرفر وهمي لمنع البوت من النوم ---
class DummyHTTPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("البوت يعمل الآن بالنظام السحابي المتعدد!".encode('utf-8'))

def run_dummy_server():
    PORT = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", PORT), DummyHTTPServer) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- إعدادات البوت والاشتراك الإجباري ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8499856454:AAHB49UPTI7Q4sF0OyMr-GhBPOIVk9aBRRo") 
CHANNELS = ["@iq_2a1"]

bot = telebot.TeleBot(BOT_TOKEN)

def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return True
    return True

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not check_subscription(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="اضغط هنا للاشتراك بالقناة 📢", url="https://t.me/iq_2a1")
        markup.add(btn)
        bot.reply_to(message, "⚠️ عذراً عزيزي، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت!", reply_markup=markup)
        return
        
    bot.reply_to(message, "👋 أهلاً بك! لقد تم ربط البوت بـ 5 سيرفرات سحابية خارجية لتخطي الحظر. أرسل لي أي رابط!")

# دالة ذكية للبحث في 5 سيرفرات مختلفة لتخطي الحظر
def get_video_url(url):
    apis = [
        "https://co.wuk.sh/api/json",
        "https://api.cobalt.tools/api/json",
        "https://cobalt.qwyre.com/api/json",
        "https://api.cobalt.tools/",
        "https://co.wuk.sh/"
    ]
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    payload = {"url": url}
    
    for api in apis:
        try:
            res = requests.post(api, json=payload, headers=headers, timeout=12)
            if res.status_code == 200:
                data = res.json()
                if 'url' in data:
                    return data['url']
        except Exception:
            continue # إذا فشل السيرفر، انتقل للذي يليه فوراً
    return None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not check_subscription(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="اضغط هنا للاشتراك بالقناة 📢", url="https://t.me/iq_2a1")
        markup.add(btn)
        bot.reply_to(message, "⚠️ عذراً عزيزي، لا يمكنك التحميل حتى تشترك في القناة أولاً!", reply_markup=markup)
        return

    url = message.text
    url_lower = url.lower()
    
    if any(domain in url_lower for domain in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "facebook.com", "fb.watch", "x.com", "twitter.com"]):
        status_msg = bot.reply_to(message, "🚀 جاري البحث عن الفيديو في السيرفرات السحابية...")
        
        direct_url = get_video_url(url)
        
        if direct_url:
            try:
                bot.edit_message_text("📥 تم العثور على الفيديو! جاري الإرسال لتيليجرام...", message.chat.id, status_msg.message_id)
                bot.send_video(message.chat.id, direct_url, reply_to_message_id=message.message_id)
                bot.delete_message(message.chat.id, status_msg.message_id)
            except Exception as e:
                bot.edit_message_text("❌ عذراً، حجم الفيديو كبير جداً أو أن تيليجرام يرفض استقباله.", message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ عذراً، جميع السيرفرات محظورة حالياً من هذه المنصة (يوتيوب/انستغرام حدثت حمايتها للتو). جرب مقطعاً آخر.", message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "⚠️ أرسل رابطاً صحيحاً من المنصات المعروفة.")

if __name__ == "__main__":
    bot.infinity_polling()
