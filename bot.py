import os
import threading
import http.server
import socketserver
import telebot
import yt_dlp
import requests
import re

# --- سيرفر وهمي لمنع البوت من النوم ---
class DummyHTTPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("البوت يعمل بنظام تخطي حظر انستغرام المتقدم!".encode('utf-8'))

def run_dummy_server():
    PORT = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", PORT), DummyHTTPServer) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- إعدادات البوت والاشتراك الإجباري ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8499856454:AAHB49UPTI7Q4sF0OyMr-GhBPOIVk9aBRRo") 
CHANNELS = ["@iq_2a1"]

bot = telebot.TeleBot(BOT_TOKEN)

def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return True
    return True

# دالة ذكية لتخطي حظر انستغرام عبر سيرفرات ddinstagram الوسيطة
def get_instagram_video_url(url):
    try:
        # تنظيف الرابط وتحويله إلى السيرفر الوسيط غير المحظور
        cleaned_url = url.replace("www.", "").replace("instagram.com", "ddinstagram.com")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(cleaned_url, headers=headers, timeout=12)
        if response.status_code == 200:
            html = response.text
            # البحث عن رابط الفيديو المباشر في الميتا تاغ الخاص بالصفحة
            match = re.search(r'<meta\s+property=["\']og:video["\']\s+content=["\'](.*?)["\']', html)
            if match:
                video_url = match.group(1)
                return video_url.replace("&amp;", "&")
    except Exception as e:
        print(f"Instagram Proxy Error: {e}")
    return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not check_subscription(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="اضغط هنا للاشتراك بالقناة 📢", url="https://t.me/iq_2a1")
        markup.add(btn)
        bot.reply_to(message, "⚠️ عذراً عزيزي، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت!", reply_markup=markup)
        return
        
    bot.reply_to(message, "👋 أهلاً بك! تم حل مشكلة انستغرام كلياً وتثبيت تيك توك. أرسل لي أي رابط الآن.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not check_subscription(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="اضغط هنا للاشتراك بالقناة 📢", url="https://t.me/iq_2a1")
        markup.add(btn)
        bot.reply_to(message, "⚠️ عذراً عزيزي، لا يمكنك التحميل حتى تشترك في القناة أولاً!", reply_markup=markup)
        return

    url = message.text
    url_lower = url.lower()
    
    if any(domain in url_lower for domain in ["tiktok.com", "instagram.com", "facebook.com", "fb.watch"]):
        status_msg = bot.reply_to(message, "🚀 جاري سحب مقطع الفيديو...")
        
        # --- أولاً: معالجة خاصة وفورية لانستغرام لتخطي حظر السيرفر ---
        if "instagram.com" in url_lower:
            direct_video = get_instagram_video_url(url)
            if direct_video:
                try:
                    bot.send_video(message.chat.id, direct_video, reply_to_message_id=message.message_id)
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    return
                except Exception:
                    pass # إذا فشل الإرسال المباشر ينتقل للطريقة الاحتياطية بالأسفل
        
        # --- ثانياً: معالجة تيك توك والمنصات الأخرى بالطريقة العادية والمستقرة ---
        ydl_opts = {
            'format': 'b[ext=mp4]/best', 
            'outtmpl': f'video_{message.chat.id}_%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
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
            bot.edit_message_text("❌ عذراً، لا يمكن تحميل هذا المقطع حالياً. تأكد أن الحساب عام وليس خاصاً (Private).", message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "⚠️ أرسل رابطاً صحيحاً من تيك توك أو انستغرام أو فيسبوك.")

if __name__ == "__main__":
    bot.infinity_polling()
