import os
import telebot
from yt_dlp import YoutubeDL
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ⚠️ ضع توكن البوت الخاص بك هنا
BOT_TOKEN = "8499856454:AAHB49UPTI7Q4sF0OyMr-GhBPOIVk9aBRRo"
CHANNEL_USERNAME = "@iq_2a1" 

bot = telebot.TeleBot(BOT_TOKEN)

# 🌍 سيرفر وهمي لضمان بقاء البوت أونلاين 24/7
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Bot is running successfully 24/7!</h1>")

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
    except Exception as e:
        return True

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    if not is_user_subscribed(user_id):
        bot.reply_to(message, f"📢 عذراً عزيزي، يجب عليك الاشتراك في قناة البوت أولاً لاستخدامه:\n👉 {CHANNEL_USERNAME}\n\nبعد الاشتراك، أرسل /start مجدداً!")
        return

    welcome_msg = (
        "👋 أهلاً بك في بوت التحميل العالمي المطور!\n\n"
        "📥 أرسل لي أي رابط فيديو أو موسيقى من المنصات التالية:\n"
        "🔹 TikTok  🔹 Instagram  🔹 YouTube  🔹 Facebook\n\n"
        "⚙️ تم تحسين جودة وحجم مقاطع يوتيوب تلقائياً (480p) لضمان السرعة القصوى!"
    )
    bot.reply_to(message, welcome_msg)

@bot.message_handler(func=lambda message: True)
def process_download(message):
    user_id = message.from_user.id
    if not is_user_subscribed(user_id):
        bot.reply_to(message, f"📢 عذراً، لا يمكنك التحميل قبل الاشتراك في القناة:\n👉 {CHANNEL_USERNAME}")
        return

    url = message.text
    if not url.startswith("http"):
        bot.reply_to(message, "❌ من فضلك أرسل رابطاً صحيحاً يبدأ بـ http أو https.")
        return

    status = bot.reply_to(message, "⏳ جاري فحص الرابط وتخطي حماية يوتيوب للتحميل...")

    # ⚙️ إعدادات سحرية جديدة: محاكاة هاتف أندرويد لتخطي حظر السيرفرات وتجاهل أخطاء الشهادات
    ydl_opts = {
        'format': 'best[height<=480][ext=mp4]/best', 
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'max_filesize': 48 * 1024 * 1024,
        'quiet': True,
        'nocheckcertificate': True, # تخطي مشاكل شهادات الأمان
        'geo_bypass': True, # تخطي الحظر الجغرافي
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}} # خدعة إقناع يوتيوب أننا هاتف أندرويد
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'فيديو محمل')

        bot.edit_message_text("🚀 اكتمل التحميل! جاري رفع الفيديو إليك الآن...", chat_id=message.chat.id, message_id=status.message_id)
        
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=f"🎬 {title}\n\n✨ تم التحميل بنجاح.")
        
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(chat_id=message.chat.id, message_id=status.message_id)

    except Exception as e:
        err = str(e)
        # الآن سيقوم البوت بطباعة الخطأ الفعلي القادم من يوتيوب لكي نعرف حله فوراً
        error_text = f"❌ حدث خطأ من المصدر (يوتيوب). التفاصيل البرمجية:\n\n`{err[:200]}`"
        bot.edit_message_text(error_text, chat_id=message.chat.id, message_id=status.message_id, parse_mode="Markdown")
        
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

try:
    bot.remove_webhook()
except:
    pass

bot.infinity_polling(timeout=20, long_polling_timeout=10)
