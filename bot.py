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
        self.wfile.write("البوت يعمل بنجاح ومباشرة بدون وسطاء!".encode('utf-8'))

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
    bot.reply_to(message, "👋 أهلاً بك! لقد عدنا للتحميل المباشر. أرسل لي أي رابط!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    
    # تحويل الرابط لنص صغير لتجنب مشاكل الحروف الكبيرة
    url_lower = url.lower()
    
    if any(domain in url_lower for domain in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "facebook.com", "x.com", "twitter.com"]):
        status_msg = bot.reply_to(message, "🚀 جاري التحميل المباشر الآن...")
        
        # إعدادات التحميل (اختيار صيغة مدمجة لا تحتاج برامج خارجية)
        ydl_opts = {
            'format': 'b[ext=mp4]/b', 
            'outtmpl': f'video_{message.chat.id}_%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
        # التأكد من مسار الكوكيز بشكل صحيح وقراءته
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cookies_path = os.path.join(current_dir, 'cookies.txt')
        
        if os.path.exists(cookies_path):
            ydl_opts['cookiefile'] = cookies_path
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                bot.edit_message_text("📥 اكتمل التحميل! جاري إرسال الفيديو...", message.chat.id, status_msg.message_id)
                
                with open(filename, 'rb') as video:
                    bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
                    
                if os.path.exists(filename):
                    os.remove(filename)
                bot.delete_message(message.chat.id, status_msg.message_id)
                
        except Exception as e:
            print(f"Error details: {str(e)}")
            bot.edit_message_text("❌ عذراً، الرابط غير مدعوم أو أن المنصة تمنع التحميل حالياً.", message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "⚠️ أرسل رابطاً صحيحاً من المنصات المعروفة.")

if __name__ == "__main__":
    bot.infinity_polling()
