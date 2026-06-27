import os
import threading
import http.server
import socketserver
import telebot
import yt_dlp

# --- سيرفر وهمي لمنع Render من إغلاق البوت ---
class DummyHTTPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("البوت يعمل بنجاح!".encode('utf-8'))

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
    bot.reply_to(message, "👋 أهلاً بك! أرسل لي أي رابط فيديو لتحميله فوراً.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    
    if any(domain in url for domain in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "facebook.com"]):
        status_msg = bot.reply_to(message, "🚀 جاري معالجة الرابط (بتقنية التخفي)...")
        
        # التعديل الأهم: التنكر كجهاز أندرويد لتخطي حظر يوتيوب بدون كوكيز
        ydl_opts = {
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'extractor_args': {'youtube': ['player_client=android']}, # سطر التخفي السحري
            'noplaylist': True,
            'quiet': True
        }
        
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            with open(filename, 'rb') as video:
                bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
                
            if os.path.exists(filename):
                os.remove(filename)
                
            bot.delete_message(message.chat.id, status_msg.message_id)
            
        except Exception as e:
            bot.edit_message_text(f"❌ حدث خطأ:\n`{str(e)}`", message.chat.id, status_msg.message_id, parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ أرسل رابط صحيح من يوتيوب أو المنصات المدعومة.")

if __name__ == "__main__":
    bot.infinity_polling()
