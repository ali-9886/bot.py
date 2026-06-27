import os
import threading
import http.server
import socketserver
import telebot
import yt_dlp

# --- 1. حل مشكلة إغلاق السيرفر في Render (Port Binding) ---
class DummyHTTPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("البوت يعمل بنجاح وبدون مشاكل!".encode('utf-8'))

def run_dummy_server():
    PORT = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", PORT), DummyHTTPServer) as httpd:
        httpd.serve_forever()

# تشغيل سيرفر وهمي في الخلفية لإرضاء Render ومنع الخطأ المعتاد
threading.Thread(target=run_dummy_server, daemon=True).start()


# --- 2. إعدادات وتشغيل بوت تيليجرام ---
# استبدل النص أدناه بـ توكن بوتك الحقيقي (Token) المستخرج من BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8499856454:AAHB49UPTI7Q4sF0OyMr-GhBPOIVk9aBRRo") 
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 أهلاً بك في بوت التحميل العالمي المطور!\n\n"
        "🎵 أرسل لي أي رابط فيديو أو موسيقى من المنصات التالية:\n"
        "🔹 TikTok  🔹 Instagram  🔹 YouTube  🔹 Facebook\n\n"
        "⚙️ تم تحسين جودة التحميل تلقائياً لضمان السرعة القصوى وتفادي القيود!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    
    # التحقق من أن الرسالة تحتوي على رابط من منصة مدعومة
    if any(domain in url for domain in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "facebook.com"]):
        status_msg = bot.reply_to(message, "🚀 جاري معالجة الرابط وتحميل الفيديو إليك...")
        
        # إعدادات مكتبة yt-dlp الاحترافية
        ydl_opts = {
            'format': 'best',  # التعديل النهائي لحل مشكلة Requested format is not available
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'cookiefile': 'cookies.txt',  # اعتماد ملف الكوكيز المرفوع لتجاوز حظر يوتيوب
            'noplaylist': True,
        }
        
        # إنشاء مجلد مؤقت للتحميلات إذا لم يكن موجوداً
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            # إرسال ملف الفيديو مباشرة إلى المحادثة
            with open(filename, 'rb') as video:
                bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
                
            # تنظيف السيرفر وحذف الفيديو لتوفير المساحة بعد الإرسال
            if os.path.exists(filename):
                os.remove(filename)
                
            # حذف رسالة الانتظار
            bot.delete_message(message.chat.id, status_msg.message_id)
            
        except Exception as e:
            error_text = str(e)
            if "Sign in to confirm you're not a bot" in error_text:
                bot.edit_message_text("❌ حدث خطأ: يوتيوب يطلب تحديث ملف الكوكيز cookies.txt الخاص بك.", message.chat.id, status_msg.message_id)
            else:
                bot.edit_message_text(f"❌ حدث خطأ أثناء معالجة الرابط.\n\nالتفاصيل البرمجية:\n`{error_text}`", message.chat.id, status_msg.message_id, parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ الرجاء إرسال رابط صحيح من منصة مدعومة (YouTube, TikTok, Instagram).")

if __name__ == "__main__":
    print("البوت يعمل الآن ومستعد تماماً لاستقبال الروابط...")
    bot.infinity_polling()
