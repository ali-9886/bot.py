import os
import telebot
from yt_dlp import YoutubeDL
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ⚠️ ضع توكن البوت الخاص بك هنا بين علامتي التنصيص
BOT_TOKEN = "8499856454:AAHB49UPTI7Q4sF0OyMr-GhBPOIVk9aBRRo"
CHANNEL_USERNAME = "@iq_2a1"  # معرف قناة الاشتراك الإجباري الخاص بك

bot = telebot.TeleBot(BOT_TOKEN)

# 🌍 سيرفر وهمي ذكي لتخطي فحص المنافذ (Ports) في رندر لضمان التشغيل 24/7 دون توقف تلقائي
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

threading.Thread(target=run_server, daemon=True).start()

# التأكد من وجود مجلد مؤقت للتحميلات
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# دالة فحص إذا كان المستخدم مشتركاً في القناة أم لا
def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"تنبيه فحص الاشتراك: {e}")
        # في حال عدم تمكن البوت من الفحص (مثلاً لم يتم إضافته كمشرف في القناة بعد) سيعمل مؤقتاً
        return True

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    
    # تحقق الاشتراك الإجباري عند الضغط على start
    if not is_user_subscribed(user_id):
        bot.reply_to(message, f"📢 عذراً عزيزي، يجب عليك الاشتراك في قناة البوت أولاً لاستخدامه:\n👉 {CHANNEL_USERNAME}\n\nبعد الاشتراك، أرسل /start مجدداً لتفعيل البوت!")
        return

    welcome_msg = (
        "👋 أهلاً بك في بوت التحميل العالمي المطور!\n\n"
        "📥 أرسل لي أي رابط فيديو أو موسيقى من المنصات التالية:\n"
        "🔹 TikTok  🔹 Instagram  🔹 YouTube  🔹 Facebook\n\n"
        "⚙️ تم تحسين جودة وحجم مقاطع يوتيوب تلقائياً (480p) لضمان السرعة القصوى وتفادي القيود!"
    )
    bot.reply_to(message, welcome_msg)

@bot.message_handler(func=lambda message: True)
def process_download(message):
    user_id = message.from_user.id
    
    # تحقق الاشتراك الإجباري قبل تنفيذ أي عملية تحميل
    if not is_user_subscribed(user_id):
        bot.reply_to(message, f"📢 عذراً، لا يمكنك التحميل قبل الاشتراك في القناة المخصصة للبوت:\n👉 {CHANNEL_USERNAME}\n\nاشترك بالقناة ثم أرسل الرابط مجدداً!")
        return

    url = message.text
    if not url.startswith("http"):
        bot.reply_to(message, "❌ من فضلك أرسل رابطاً صحيحاً يبدأ بـ http أو https.")
        return

    status = bot.reply_to(message, "⏳ جاري فحص الرابط وتقليل حجم الفيديو للتحميل السريع بدون قيود...")

    # ⚙️ الإعداد السحري لتقليل الحجم: يجبر يوتيوب والمنصات على جودة 480p أو أقل للحفاظ على حجم صغير خفيف
    ydl_opts = {
        'format': 'best[height<=480][ext=mp4]/best[ext=mp4]/best', 
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'max_filesize': 48 * 1024 * 1024, # حد أقصى 48 ميجا ليقبل التليجرام رفعه فوراً
        'quiet': True,
        'no_warnings': True,
        'source_address': '0.0.0.0' # حيلة لتفادي حظر بروتوكولات الـ IPv6 في يوتيوب أحياناً
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'فيديو محمل')

        bot.edit_message_text("🚀 اكتمل التحميل والضغط بنجاح! جاري رفع الفيديو إليك الآن...", chat_id=message.chat.id, message_id=status.message_id)
        
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=f"🎬 {title}\n\n✨ تم التحميل والرفع بنجاح عبر سيرفرك المستمر.")
        
        # تنظيف السيرفر فوراً
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(chat_id=message.chat.id, message_id=status.message_id)

    except Exception as e:
        err = str(e)
        if "max_filesize" in err or "too large" in err:
            bot.edit_message_text("❌ حجم الفيديو حتى بعد الضغط أكبر من حد التليجرام المجاني (48 ميجابايت).", chat_id=message.chat.id, message_id=status.message_id)
        else:
            bot.edit_message_text("❌ حدث خطأ أثناء معالجة الرابط. تأكد أن الفيديو عام وليس خاصاً وجرب رابطاً آخر.", chat_id=message.chat.id, message_id=status.message_id)
        
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

try:
    bot.remove_webhook()
except:
    pass

print("🚀 البوت المطور جاهز ويعمل الآن بنجاح أونلاين...")
bot.infinity_polling(timeout=20, long_polling_timeout=10)
