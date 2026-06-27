import os
import telebot
from yt_dlp import YoutubeDL
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ⚠️ ضع توكن البوت الخاص بك هنا
BOT_TOKEN = "8499856454:AAHB49UPTI7Q4sF0OyMr-GhBPOIVk9aBRRo"
CHANNEL_USERNAME = "@iq_2a1" 

bot = telebot.TeleBot(BOT_TOKEN)

# 🌍 سيرفر وهمي لبقاء البوت أونلاين
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Bot is running 24/7 with Cookies!</h1>")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

if not os.path.exists('downloads'):
    os.makedirs('downloads')

def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return True

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    if not is_user_subscribed(user_id):
        bot.reply_to(message, f"📢 عذراً عزيزي، يجب عليك الاشتراك في قناة البوت أولاً:\n👉 {CHANNEL_USERNAME}\n\nبعد الاشتراك، أرسل /start مجدداً!")
        return
    bot.reply_to(message, "👋 أهلاً بك! أرسل لي أي رابط من يوتيوب، تيك توك، انستغرام، أو فيسبوك وسأقوم بتحميله مباشرة.")

@bot.message_handler(func=lambda message: True)
def process_download(message):
    user_id = message.from_user.id
    if not is_user_subscribed(user_id):
        bot.reply_to(message, f"📢 عذراً، يجب الاشتراك أولاً:\n👉 {CHANNEL_USERNAME}")
        return

    url = message.text
    if not url.startswith("http"):
        bot.reply_to(message, "❌ أرسل رابطاً صحيحاً.")
        return

    status = bot.reply_to(message, "⏳ جاري التحميل المباشر...")

    # تنظيف الرابط
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"

    # ⚙️ السر هنا: استخدام ملف الكوكيز لتخطي حظر يوتيوب نهائياً
    ydl_opts = {
        'format': 'best[height<=480][ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'max_filesize': 48 * 1024 * 1024,
        'quiet': True,
        'nocheckcertificate': True,
        'cookiefile': 'cookies.txt' # قراءة بصمة الدخول التي رفعناها
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'فيديو محمل')

        bot.edit_message_text("🚀 جاري رفع الفيديو إليك...", chat_id=message.chat.id, message_id=status.message_id)
        
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=f"🎬 {title}")
        
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(chat_id=message.chat.id, message_id=status.message_id)

    except Exception as e:
        # أعدت كتابة هذا السطر ليطبع لك المشكلة الحقيقية بدلاً من الرسالة العامة
        bot.edit_message_text(f"❌ خطأ:\n`{str(e)[:200]}`", chat_id=message.chat.id, message_id=status.message_id, parse_mode="Markdown")
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

try:
    bot.remove_webhook()
except:
    pass

bot.infinity_polling(timeout=20, long_polling_timeout=10)
