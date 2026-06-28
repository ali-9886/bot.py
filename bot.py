import os
import threading
import http.server
import socketserver
import telebot
import yt_dlp
import requests
import re

# --- سيرفر وهمي لمنع البوت من النوم ولدعمه عبر UptimeRobot ---
class DummyHTTPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("البوت المستقر يعمل بنظام تخطي الحظر المتقدم!".encode('utf-8'))

def run_dummy_server():
    PORT = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", PORT), DummyHTTPServer) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- إعدادات البوت وقناة الاشتراك الإجباري ---
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

# دالة كسر حظر انستغرام وسحب الفيديو المباشر بدون سيرفرات وسيطة معقدة
def get_instagram_direct_url(url):
    try:
        # تحويل الرابط إلى السيرفر الوسيط المستقر لعرض البيانات النظيفة
        proxy_url = url.replace("instagram.com", "ddinstagram.com").replace("www.", "")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        res = requests.get(proxy_url, headers=headers, timeout=10)
        if res.status_code == 200:
            # البحث عن رابط الفيديو الفعلي داخل الميتا تاغ لصفحة انستغرام المخفية
            match = re.search(r'<meta\s+property=["\']og:video["\']\s+content=["\'](.*?)["\']', res.text)
            if match:
                return match.group(1).replace("&amp;", "&")
            match2 = re.search(r'<meta\s+name=["\']twitter:player:stream["\']\s+content=["\'](.*?)["\']', res.text)
            if match2:
                return match2.group(1).replace("&amp;", "&")
    except:
        pass
    return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not check_subscription(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="اضغط هنا للاشتراك بالقناة 📢", url="https://t.me/iq_2a1")
        markup.add(btn)
        bot.reply_to(message, "⚠️ عذراً عزيزي، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت!", reply_markup=markup)
        return
    bot.reply_to(message, "👋 أهلاً بك! تم تحديث نظام انستغرام إلى جدار الحماية الذكي. أرسل أي رابط الآن (تيك توك أو انستغرام).")

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
    
    if any(domain in url_lower for domain in ["tiktok.com", "instagram.com", "facebook.com", "fb.watch", "youtube.com", "youtu.be"]):
        status_msg = bot.reply_to(message, "🚀 جاري التحميل والمعالجة الفورية بدون حظر...")
        
        # --- أولاً: التعامل الذكي والصارم مع انستغرام كسر حظر 100% ---
        if "instagram.com" in url_lower:
            direct_video_url = get_instagram_direct_url(url)
            if direct_video_url:
                try:
                    # إرسال الفيديو مباشرة لتيليجرام عبر الرابط لتوفير سيرفر Render بالكامل
                    bot.send_video(message.chat.id, direct_video_url, reply_to_message_id=message.message_id)
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    return
                except:
                    # خطة بديلة في حال فشل الإرسال المباشر بالرابط: نقوم بتحميله وإرساله كملف
                    try:
                        video_data = requests.get(direct_video_url, timeout=20).content
                        filename = f"insta_{message.chat.id}.mp4"
                        with open(filename, 'wb') as f:
                            f.write(video_data)
                        with open(filename, 'rb') as video_file:
                            bot.send_video(message.chat.id, video_file, reply_to_message_id=message.message_id)
                        if os.path.exists(filename): os.remove(filename)
                        bot.delete_message(message.chat.id, status_msg.message_id)
                        return
                    except:
                        if os.path.exists(filename): os.remove(filename)
            
            bot.edit_message_text("❌ عذراً، هذا المقطع محمي أو خاص بحساب صاحبه. تأكد أن الحساب عام (Public).", message.chat.id, status_msg.message_id)
            return

        # --- ثانياً: تيك توك وبقية المنصات بالنظام التقليدي المستقر ---
        ydl_opts = {
            'format': 'b[ext=mp4]/best', 
            'outtmpl': f'video_{message.chat.id}_%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                dl_filename = ydl.prepare_filename(info)
                
                with open(dl_filename, 'rb') as video:
                    bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
                    
                if os.path.exists(dl_filename):
                    os.remove(dl_filename)
                bot.delete_message(message.chat.id, status_msg.message_id)
        except Exception:
            bot.edit_message_text("❌ عذراً، فشل تحميل هذا المقطع. تأكد من صحة الرابط وعموميته.", message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "⚠️ أرسل رابطاً صحيحاً ومدعوماً.")

if __name__ == "__main__":
    bot.infinity_polling()
