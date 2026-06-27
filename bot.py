import os
import threading
import http.server
import socketserver
import telebot
import requests

# --- سيرفر وهمي لمنع Render من إغلاق البوت ---
class DummyHTTPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("البوت يعمل عبر السيرفرات البديلة بنجاح!".encode('utf-8'))

def run_dummy_server():
    PORT = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", PORT), DummyHTTPServer) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- إعدادات البوت ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8499856454:AAHB49UPTI7Q4sF0OyMr-GhBPOIVk9aBRRo") 
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 أهلاً بك! أنا أعمل الآن بنظام السيرفرات البديلة (بدون حظر). أرسل لي أي رابط فيديو لتحميله.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    
    if any(domain in url for domain in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "facebook.com", "x.com", "twitter.com"]):
        status_msg = bot.reply_to(message, "🚀 جاري البحث في السيرفرات البديلة لجلب الفيديو...")
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        data = {"url": url}
        
        # قائمة السيرفرات البديلة التي تعمل بدون قيود
        api_endpoints = [
            "https://co.wuk.sh/api/json",
            "https://ca.haloz.at/api/json",
            "https://cobalt-api.ayo.tf/api/json",
            "https://coapi.kelig.me/api/json"
        ]
        
        video_url = None
        
        # البوت سيجرب السيرفرات واحداً تلو الآخر حتى ينجح
        for api in api_endpoints:
            try:
                response = requests.post(api, json=data, headers=headers, timeout=15)
                if response.status_code == 200:
                    video_url = response.json().get('url')
                    if video_url:
                        break # نجحنا! نوقف البحث
            except:
                continue # إذا فشل هذا السيرفر، انتقل للسيرفر الذي يليه
                
        if video_url:
            bot.edit_message_text("📥 تم العثور على الفيديو! جاري معالجته وإرساله لك...", message.chat.id, status_msg.message_id)
            
            try:
                r = requests.get(video_url, stream=True)
                filename = f"video_{message.chat.id}.mp4"
                
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
                with open(filename, 'rb') as video:
                    bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
                    
                if os.path.exists(filename):
                    os.remove(filename)
                bot.delete_message(message.chat.id, status_msg.message_id)
                
            except Exception as e:
                bot.edit_message_text("❌ حدث خطأ أثناء إرسال الفيديو كملف لتيليجرام.", message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ عذراً، جميع السيرفرات المجانية البديلة مشغولة الآن، أو أن الرابط غير مدعوم. حاول مرة أخرى بعد قليل.", message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "⚠️ أرسل رابط صحيح من يوتيوب، تيك توك، انستغرام، أو تويتر.")

if __name__ == "__main__":
    bot.infinity_polling()
