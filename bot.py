import os
import threading
import http.server
import socketserver
import telebot
import yt_dlp
import requests

# --- سيرفر وهمي لمنع البوت من النوم لدعمه عبر UptimeRobot ---
class DummyHTTPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("البوت الهجين يعمل بأعلى كفاءة لجميع المنصات!".encode('utf-8'))

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

# دالة سحابية متطورة لتنزيل فيديو انستغرام ويوتيوب وتخطي حظر السيرفر
def download_via_api(url, download_path):
    instances = [
        "https://api.cobalt.tools/api/json",
        "https://co.wuk.sh/api/json",
        "https://cobalt.moe/api/json"
    ]
    payload = {
        "url": url,
        "videoQuality": "720",
        "filenamePattern": "classic"
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    video_url = None
    for instance in instances:
        try:
            res = requests.post(instance, json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if 'url' in data:
                    video_url = data['url']
                    break
        except:
            continue
            
    if not video_url:
        return False

    try:
        video_res = requests.get(video_url, stream=True, timeout=30)
        if video_res.status_code == 200:
            with open(download_path, 'wb') as f:
                for chunk in video_res.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            return True
    except:
        return False
    return False

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not check_subscription(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="اضغط هنا للاشتراك بالقناة 📢", url="https://t.me/iq_2a1")
        markup.add(btn)
        bot.reply_to(message, "⚠️ عذراً عزيزي، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت!", reply_markup=markup)
        return
    bot.reply_to(message, "👋 أهلاً بك! تم تحديث البوت كلياً لحل مشكلة انستغرام ويوتيوب وتثبيت تيك توك. أرسل أي رابط الآن!")

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
        status_msg = bot.reply_to(message, "🚀 جاري التحميل والمعالجة الفورية...")
        filename = f"video_{message.chat.id}.mp4"
        
        # إذا كان الرابط من انستغرام أو يوتيوب، يتم استخدام النظام السحابي لتجنب الحظر
        if any(x in url_lower for x in ["instagram.com", "youtube.com", "youtu.be"]):
            success = download_via_api(url, filename)
            if success and os.path.exists(filename):
                try:
                    with open(filename, 'rb') as video:
                        bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
                    os.remove(filename)
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    return
                except Exception:
                    if os.path.exists(filename): os.remove(filename)
                    bot.edit_message_text("❌ فشل إرسال الفيديو، قد يكون حجمه كبيراً جداً على تيليجرام.", message.chat.id, status_msg.message_id)
                    return
            else:
                bot.edit_message_text("❌ فشل السيرفر في جلب المقطع، تأكد من أن الرابط عام وصحيح وجرب مرة أخرى.", message.chat.id, status_msg.message_id)
                return

        # لمنصة تيك توك والمنصات الأخرى، يستمر التحميل التقليدي المستقر
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
            bot.edit_message_text("❌ عذراً، فشل تحميل هذا المقطع. تأكد من صحة الرابط.", message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "⚠️ أرسل رابطاً صحيحاً من المنصات المدعومة.")

if __name__ == "__main__":
    bot.infinity_polling()
