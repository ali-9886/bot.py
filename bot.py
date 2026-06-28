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
import os
import telebot
from yt_dlp import YoutubeDL
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ⚠️ ضع توكن البوت الخاص بك هنا
BOT_TOKEN = "8499856454:AAHB49UPTI7Q4sF0OyMr-GhBPOIVk9aBRRo"
CHANNEL_USERNAME = "@iq_2a1" 

bot = telebot.TeleBot(BOT_TOKEN)

# 🌍 سيرفر وهمي لتخطي فحص المنافذ في Render وبقاء البوت يعمل 24/7
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Downloader Bot is fully active!</h1>")

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
        bot.reply_to(message, f"📢 عذراً عزيزي، يجب عليك الاشتراك في قناة البوت أولاً لاستخدامه:\n👉 {CHANNEL_USERNAME}\n\nبعد الاشتراك، أرسل /start مجدداً!")
        return

    welcome_msg = (
        "👋 أهلاً بك في بوت التحميل المباشر الشامل!\n\n"
        "📥 أرسل لي رابط الفيديو من أي منصة وسأقوم بتحميله وإرساله لك كملف مباشر فوراً:\n"
        "🔹 YouTube  🔹 TikTok  🔹 Instagram  🔹 Facebook"
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
        bot.reply_to(message, "❌ من فضلك أرسل رابطاً صحيحاً.")
        return

    status = bot.reply_to(message, "⏳ جاري بدء التحميل المباشر وتخطي الحجب السحابي...")

    # تنظيف وتجهيز روابط يوتيوب
    cleaned_url = url
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
        cleaned_url = f"https://www.youtube.com/watch?v={video_id}"

    # ⚙️ الإعداد السحري لكسر الحظر بالاعتماد على عملاء الويب الموثوقين وتوليد توكن زائر تلقائي
    ydl_opts = {
        'format': 'best[height=480][ext=mp4]/best[height<=480][ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'max_filesize': 48 * 1024 * 1024,
        'quiet': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'mweb'], # استخدام مشغلات متصفحات الكمبيوتر والهاتف الرسمية
                'po_token': 'web+mn6_EA3gXv:dummy_token', # حيلة توليد توكن تخطي إثبات الروبوت الافتراضي
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://www.youtube.com',
        }
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(cleaned_url, download=True)
            filename = ydl.prepare_filename(info)
            
            # معالجة امتدادات الفيديو المدمج
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                if os.path.exists(base + ".mp4"):
                    filename = base + ".mp4"
                elif os.path.exists(base + ".mkv"):
                    filename = base + ".mkv"

            title = info.get('title', 'فيديو محمل')

        bot.edit_message_text("🚀 اكتمل التحميل المباشر بنجاح! جاري رفع الفيديو إليك الآن...", chat_id=message.chat.id, message_id=status.message_id)
        
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=f"🎬 {title}\n\n✨ تم التحميل المباشر بنجاح.")
        
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(chat_id=message.chat.id, message_id=status.message_id)

    except Exception as e:
        bot.edit_message_text("❌ حدث خطأ أثناء التحميل. تأكد من أن الرابط يعمل بشكل صحيح وحاول مرة أخرى.", chat_id=message.chat.id, message_id=status.message_id)
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

try:
    bot.remove_webhook()
except:
    pass

bot.infinity_polling(timeout=20, long_polling_timeout=10)
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- إعدادات البوت ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8499856454:AAHB49UPTI7Q4sF0OyMr-GhBPOIVk9aBRRo") 
bot = telebot.TeleBot(BOT_TOKEN)
CHANNELS = ["@iq_2a1"]

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
