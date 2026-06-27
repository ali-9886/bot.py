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
        self.wfile.write("البوت يعمل عبر API بنجاح!".encode('utf-8'))

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
    bot.reply_to(message, "👋 أهلاً بك! أنا أعمل الآن بنظام (API) الخارجي. أرسل لي أي رابط فيديو لتحميله.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    
    if any(domain in url for domain in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "facebook.com", "x.com", "twitter.com"]):
        status_msg = bot.reply_to(message, "🚀 جاري الاتصال بالسيرفر الخارجي لجلب الفيديو...")
        
        try:
            # استخدام واجهة Cobalt API المفتوحة للتحميل متخطية حظر يوتيوب
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            data = {"url": url}
            
            response = requests.post("https://api.cobalt.tools/api/json", json=data, headers=headers)
            
            if response.status_code == 200:
                video_url = response.json().get('url')
                if video_url:
                    bot.edit_message_text("📥 تم العثور على الفيديو! جاري معالجته وإرساله...", message.chat.id, status_msg.message_id)
                    
                    # تحميل الفيديو إلى السيرفر مؤقتاً ثم إرساله لك
                    r = requests.get(video_url, stream=True)
                    filename = f"video_{message.chat.id}.mp4"
                    
                    with open(filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                            
                    with open(filename, 'rb') as video:
                        bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
                        
                    # مسح الملف بعد الإرسال لتوفير المساحة
                    if os.path.exists(filename):
                        os.remove(filename)
                    bot.delete_message(message.chat.id, status_msg.message_id)
                else:
                    bot.edit_message_text("❌ لم يتمكن السيرفر الخارجي من استخراج الرابط.", message.chat.id, status_msg.message_id)
            else:
                bot.edit_message_text(f"❌ عذراً، واجهنا مشكلة مع السيرفر الخارجي. (كود: {response.status_code})", message.chat.id, status_msg.message_id)
                
        except Exception as e:
            bot.edit_message_text(f"❌ حدث خطأ غير متوقع:\n`{str(e)}`", message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "⚠️ أرسل رابط صحيح من يوتيوب، تيك توك، انستغرام، أو تويتر.")

if __name__ == "__main__":
    bot.infinity_polling()
