import os
import telebot
from yt_dlp import YoutubeDL
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ⚠️ ضع توكن البوت الخاص بك هنا
BOT_TOKEN = "8499856454:AAHB49UPTI7Q4sF0OyMr-GhBPOIVk9aBRRo"
CHANNEL_USERNAME = "@iq_2a1" 

bot = telebot.TeleBot(BOT_TOKEN)

# 🌍 سيرفر وهمي لضمان بقاء البوت أونلاين 24/7 دون توقف تلقائي من رندر
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Downloader Bot is Live 24/7!</h1>")

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
        "👋 أهلاً بك في البوت العالمي الشامل والنهائي!\n\n"
        "📥 أرسل لي أي رابط من:\n"
        "🔹 YouTube & Shorts\n"
        "🔹 TikTok  🔹 Instagram  🔹 Facebook\n\n"
        "⚙️ تم تفعيل نظام التخطي الاحترافي للحظر والقيود تلقائياً وبأقصى سرعة وضغط!"
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

    status = bot.reply_to(message, "⏳ جاري تجاوز جدار الحماية والأمان والتحميل المستقر...")

    # تعديل الروابط المختصرة لضمان فك التشفير بأعلى مستوى
    cleaned_url = url
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
        cleaned_url = f"https://www.youtube.com/watch?v={video_id}"

    # ⚙️ إعدادات قصوى لتخطي حظر "confirm you're not a bot" عن طريق دمج عدة مشغلات بديلة
    ydl_opts = {
        'format': 'best[height<=480][ext=mp4]/bestvideo[height<=480]+bestaudio/best', 
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'max_filesize': 48 * 1024 * 1024,
        'quiet': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'ignoreerrors': True,
        'no_color': True,
        'extractor_args': {
            'youtube': {
                # دمج بروتوكول مشغل الويب المخصص للأجهزة اللوحية وتلفاز الإنترنت لتفادي كشف السيرفر
                'player_client': ['tvhtml5', 'creator', 'web_embedded'],
                'skip': ['dash', 'hls', 'translated_subs']
            }
        },
        # تزييف العميل بالكامل ليعطي هوية متصفح أبل سفاري حديث بدلاً من لغة بايثون
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us',
        }
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(cleaned_url, download=True)
            if not info:
                raise Exception("تجاوز الحماية فشل مع هذا الرابط المباشر.")
            
            filename = ydl.prepare_filename(info)
            # معالجة امتدادات الدمج في حال تم تحميل جودة منفصلة
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                if os.path.exists(base + ".mp4"):
                    filename = base + ".mp4"
                elif os.path.exists(base + ".mkv"):
                    filename = base + ".mkv"

            title = info.get('title', 'فيديو محمل')

        bot.edit_message_text("🚀 نجح تخطي القيود! جاري إرسال المقطع إليك الآن...", chat_id=message.chat.id, message_id=status.message_id)
        
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=f"🎬 {title}\n\n✨ تم التحميل بأمان واستقرار.")
        
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(chat_id=message.chat.id, message_id=status.message_id)

    except Exception as e:
        # حل بديل أوتوماتيكي: إذا فشل التحميل المباشر بسبب حظر الآي بي بالكامل للسيرفر
        bot.edit_message_text("🔄 تم كشف الحظر السحابي.. جاري التحويل الفوري لمشغل الرفع السريع الجاهز...", chat_id=message.chat.id, message_id=status.message_id)
        try:
            # نوفر للمستخدم رابط تحميل خارجي مباشر ومضغوط كخيار طوارئ لتفادي التوقف تماماً إذا كان السيرفر محظور كلياً من يوتيوب
            import urllib.parse
            encoded_url = urllib.parse.quote(cleaned_url)
            bypass_link = f"https://en.savefrom.net/#url={encoded_url}"
            
            bot.edit_message_text(
                f"⚠️ يوتيوب يفرض قيوداً مشددة على السيرفرات السحابية حالياً.\n\n"
                f"💡 لتنزيل هذا المقطع فوراً وبكبسة زر واحدة اضغط هنا:\n"
                f"🔗 [اضغط هنا لتحميل الفيديو مباشرة]({bypass_link})",
                chat_id=message.chat.id, message_id=status.message_id, parse_mode="Markdown"
            )
        except:
            bot.edit_message_text("❌ عذراً، هذا المقطع محمي أو حجمه يتجاوز الحد المسموح به حالياً. جرب رابطاً آخر.", chat_id=message.chat.id, message_id=status.message_id)
        
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

try:
    bot.remove_webhook()
except:
    pass

bot.infinity_polling(timeout=20, long_polling_timeout=10)
