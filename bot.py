import os
import telebot
from yt_dlp import YoutubeDL
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ⚠️ ضع توكن البوت الخاص بك هنا بين علامتي التنصيص
BOT_TOKEN = "8499856454:AAHB49UPTI7Q4sF0OyMr-GhBPOIVk9aBRRo"

bot = telebot.TeleBot(BOT_TOKEN)

# 🌍 سيرفر وهمي ذكي لتخطي فحص المنافذ (Ports) الخاص بمنصة رندر المجانية لضمان التشغيل 24/7
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Bot is running successfully 24/7!</h1>")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    print(f"🌍 Dummy server started on port {port}")
    server.serve_forever()

# تشغيل السيرفر الوهمي في الخلفية فوراً ليرى رندر منفذاً مفتوحاً
threading.Thread(target=run_server, daemon=True).start()

# التأكد من وجود مجلد مؤقت للتحميلات
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_msg = (
        "👋 أهلاً بك في بوت التحميل العالمي المستمر!\n\n"
        "📥 أرسل لي أي رابط فيديو أو موسيقى من المنصات التالية:\n"
        "🔹 TikTok  🔹 Instagram  🔹 YouTube  🔹 Facebook\n\n"
        "🚀 يعمل البوت تلقائياً 24/7 ومستعد لخدمتك أنت وأصدقائك في أي وقت!"
    )
    bot.reply_to(message, welcome_msg)

@bot.message_handler(func=lambda message: True)
def process_download(message):
    url = message.text
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ عذراً، يجب أن ترسل رابطاً صحيحاً يبدأ بـ http أو https.")
        return

    status = bot.reply_to(message, "⏳ جاري فحص الرابط وبدء التحميل من السيرفر...")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'max_filesize': 45 * 1024 * 1024,
        'quiet': True,
        'no_warnings': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'فيديو محمل')

        bot.edit_message_text("🚀 اكتمل التحميل من المنصة! جاري رفع الفيديو إليك الآن...", chat_id=message.chat.id, message_id=status.message_id)
        
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=f"🎬 {title}\n\n✨ تم التحميل بنجاح عبر السيرفر المستمر.")
        
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(chat_id=message.chat.id, message_id=status.message_id)

    except Exception as e:
        err = str(e)
        if "max_filesize" in err or "too large" in err:
            bot.edit_message_text("❌ حجم الفيديو كبير جداً! السيرفر المجاني يدعم الملفات حتى 45 ميجابايت فقط لضمان السرعة.", chat_id=message.chat.id, message_id=status.message_id)
        else:
            bot.edit_message_text("❌ حدث خطأ أثناء معالجة الرابط. تأكد أن الحساب عام (وليس خاصاً) أو جرب مجدداً لاحقاً.", chat_id=message.chat.id, message_id=status.message_id)
        
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

try:
    bot.remove_webhook()
except:
    pass

print("🚀 البوت انطلق بنجاح ويعمل الآن أونلاين على مدار الساعة...")
bot.infinity_polling(timeout=20, long_polling_timeout=10)
