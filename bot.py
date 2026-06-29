import os
import threading
import http.server
import socketserver
import telebot
import yt_dlp
import requests

# =====================================================================
# 🛡️ ميزة منع الموت (Keep-Alive Server) لـ UptimeRobot
# =====================================================================
class AliveHTTPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("🤖 البوت شغال ومحصن 100%".encode('utf-8'))

def run_alive_server():
    PORT = int(os.environ.get("PORT", 8080))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), AliveHTTPServer) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_alive_server, daemon=True).start()

# =====================================================================
# ⚙️ إعدادات البوت والاشتراك الإجباري
# =====================================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8499856454:AAHB49UPTI7Q4sF0OyMr-GhBPOIVk9aBRRo") 
CHANNELS = ["@iq_2a1"]

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=10)

def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return True
    return True

# =====================================================================
# 📥 استقبال الأوامر
# =====================================================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not check_subscription(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="اضغط هنا ونورنا بالقناة 🌸", url="https://t.me/iq_2a1")
        markup.add(btn)
        bot.reply_to(message, "هلا بيك يا غالي ❤️\nاشترك بالقناة أولاً من الزر الجوا 👇 لتفعيل البوت.", reply_markup=markup)
        return
    bot.reply_to(message, "هلا بيك يا طيب نورت البوت! ✨\n\nدزلي أي رابط يعجبك (تيك توك، انستا، يوتيوب، فيسبوك، تويتر) وخلّي الباقي عليه! 🚀")

# =====================================================================
# 🔮 معالجة التحميل الذكي والسريع (بدون حظر)
# =====================================================================
@bot.message_handler(func=lambda message: True)
def handle_download(message):
    if not check_subscription(message.from_user.id):
        return

    url = message.text.strip()
    url_lower = url.lower()
    supported_domains = ["tiktok.com", "instagram.com", "youtube.com", "youtu.be", "facebook.com", "fb.watch", "x.com", "twitter.com", "t.me"]
    
    if any(domain in url_lower for domain in supported_domains):
        status_msg = bot.reply_to(message, "تدلل! ثواني وأجيبلك المقطع 🚀...")
        
        # 1️⃣ حل مشكلة تيك توك الجذري عبر API سريع وبدون حظر السيرفر
        if "tiktok.com" in url_lower:
            try:
                api_res = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10).json()
                if api_res and api_res.get('code') == 0:
                    video_url = api_res['data']['play']
                    bot.send_video(message.chat.id, video_url, reply_to_message_id=message.message_id, caption="تحميل موفق من تيك توك! 🎬✨")
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    return
            except:
                pass # إذا علق الـ API ينتقل للطريقة الاحتياطية تلقائياً

        # 2️⃣ حل مشكلة إنستغرام الذكي (إرسال الرابط المطور ليعرضه تيليجرام كفيديو مباشر)
        if "instagram.com" in url_lower:
            try:
                proxy_url = url.replace("instagram.com", "ddinstagram.com").replace("www.", "")
                bot.send_message(message.chat.id, f"🍿 **تفضل يا غالي، مقطع إنستغرام جاهز للمشاهدة والتحميل:**\n\n{proxy_url}", reply_to_message_id=message.message_id)
                bot.delete_message(message.chat.id, status_msg.message_id)
                return
            except:
                pass

        # 3️⃣ حل مشكلة تويتر / X الذكي
        if "x.com" in url_lower or "twitter.com" in url_lower:
            try:
                proxy_url = url.replace("x.com", "fxtwitter.com").replace("twitter.com", "fxtwitter.com")
                bot.send_message(message.chat.id, f"🍿 **تفضل يا غالي، مقطع تويتر جاهز:**\n\n{proxy_url}", reply_to_message_id=message.message_id)
                bot.delete_message(message.chat.id, status_msg.message_id)
                return
            except:
                pass

        # 4️⃣ التحميل العادي عبر السيرفر للمنصات الأخرى (يوتيوب وفيسبوك)
        filename = f"dl_{message.chat.id}_{message.message_id}.mp4"
        ydl_opts = {
            'format': 'b[ext=mp4]/best',
            'outtmpl': filename,
            'quiet': True,
            'no_warnings': True,
            'no_cache_dir': True,
            'socket_timeout': 10,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
                if os.path.exists(filename):
                    with open(filename, 'rb') as video:
                        bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id, caption="تحميل موفق يا غالي! 🍿✨")
        except:
            bot.edit_message_text("أعتذر منك يا غالي 💔، ما كدرت أحمل المقطع. تأكد أن الحساب عام وليس خاصاً.", message.chat.id, status_msg.message_id)
        finally:
            if os.path.exists(filename):
                os.remove(filename)
            try: bot.delete_message(message.chat.id, status_msg.message_id)
            except: pass
    else:
        bot.reply_to(message, "يا طيب 🥲، هذا الرابط غير مدعوم حالياً.")

# =====================================================================
# 🚀 تشغيل البوت
# =====================================================================
if __name__ == "__main__":
    try:
        bot.remove_webhook()
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"❌ خطأ: {e}")
