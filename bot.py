import os
import threading
import http.server
import socketserver
import telebot
import yt_dlp
import requests
import random

# =====================================================================
# 🛡️ ميزة منع الموت (Keep-Alive Server)
# =====================================================================
class AliveHTTPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("🤖 بوت التحميل اللطيف يعمل بكل حب وطاقة!".encode('utf-8'))

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

def get_free_proxies():
    try:
        res = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=2000", timeout=3)
        if res.status_code == 200:
            return [p.strip() for p in res.text.split("\n") if p.strip()]
    except:
        return []
    return []

# =====================================================================
# 📥 رسائل الترحيب والاشتراك الإجباري (اللطيفة)
# =====================================================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not check_subscription(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="اضغط هنا ونورنا بالقناة 🌸", url="https://t.me/iq_2a1")
        markup.add(btn)
        bot.reply_to(message, "هلا بيك يا غالي ❤️\nحتى تكدر تستخدم البوت براحتك وتستمتع بالتحميل، يا ريت تنورنا بالاشتراك بقناتنا أولاً من الزر الجوا 👇", reply_markup=markup)
        return
    
    welcome_text = (
        "هلا بيك يا طيب نورت البوت! ✨\n\n"
        "أنا هنا حتى أسهل عليك التحميل وأجيبلك أي مقطع يعجبك من:\n"
        "🔹 تيك توك (بدون حقوق)\n"
        "🔹 إنستغرام (ريلز وبوستات)\n"
        "🔹 يوتيوب (شورتس وفيديوهات)\n"
        "🔹 فيسبوك وتويتر (X) وتيليجرام\n\n"
        "بس دزلي الرابط.. وخلّي الباقي عليه! 🚀"
    )
    bot.reply_to(message, welcome_text)

# =====================================================================
# 🔮 معالجة التحميل والردود المرحة
# =====================================================================
@bot.message_handler(func=lambda message: True)
def handle_download(message):
    if not check_subscription(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="نورنا بالقناة أولاً 📢", url="https://t.me/iq_2a1")
        markup.add(btn)
        bot.reply_to(message, "عذراً يا طيب 🌸، لازم تشترك بالقناة أولاً حتى أخدمك بعيوني.", reply_markup=markup)
        return

    url = message.text
    url_lower = url.lower()
    
    supported_domains = ["tiktok.com", "instagram.com", "youtube.com", "youtu.be", "facebook.com", "fb.watch", "x.com", "twitter.com", "t.me"]
    
    if any(domain in url_lower for domain in supported_domains):
        status_msg = bot.reply_to(message, "تدلل! ثواني وأجيبلك المقطع 🚀...")
        filename = f"download_{message.chat.id}_{message.message_id}.mp4"
        
        ydl_opts = {
            'format': 'b[ext=mp4]/best',
            'outtmpl': filename,
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 8,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }

        # --- الخطة أ ---
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
                if os.path.exists(filename):
                    with open(filename, 'rb') as video:
                        bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id, caption="تحميل موفق يا غالي! 🍿✨")
                    os.remove(filename)
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    return
        except:
            if os.path.exists(filename): os.remove(filename)

        # --- الخطة ب ---
        try:
            if "instagram.com" in url_lower:
                proxy_url = url.replace("instagram.com", "ddinstagram.com").replace("www.", "")
                bot.send_video(message.chat.id, proxy_url, reply_to_message_id=message.message_id, caption="تفضل يا طيب، مشاهدة ممتعة! 🍿✨")
                bot.delete_message(message.chat.id, status_msg.message_id)
                return
            elif "x.com" in url_lower or "twitter.com" in url_lower:
                proxy_url = url.replace("x.com", "fxtwitter.com").replace("twitter.com", "fxtwitter.com")
                bot.send_video(message.chat.id, proxy_url, reply_to_message_id=message.message_id, caption="حملتلك إياه، تفضل! 🍿✨")
                bot.delete_message(message.chat.id, status_msg.message_id)
                return
        except:
            pass

        # --- الخطة ج (تخطي الحظر) ---
        bot.edit_message_text("الرابط شوية عنيد، بس دا أجربه بطريقة ثانية، دقايق من وقتك 🕵️‍♂️🔄...", message.chat.id, status_msg.message_id)
        proxies = get_free_proxies()
        random.shuffle(proxies)
        
        success = False
        for proxy in proxies[:5]:
            try:
                ydl_opts['proxy'] = f"http://{proxy}"
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(url, download=True)
                    if os.path.exists(filename):
                        with open(filename, 'rb') as video:
                            bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id, caption="تعبني بس جبته إلك، تفضل! 💪✨")
                        os.remove(filename)
                        bot.delete_message(message.chat.id, status_msg.message_id)
                        success = True
                        break
            except:
                if os.path.exists(filename): os.remove(filename)
                continue

        if not success:
            bot.edit_message_text("أعتذر منك يا غالي 💔، ما كدرت أحمل المقطع. ممكن يكون الحساب خاص (Private) أو الرابط بي مشكلة. جرب رابط ثاني وعيوني إلك!", message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "يا طيب 🥲، هذا الرابط مو من المنصات اللي أدعمها حالياً. دزلي رابط من (تيك توك، انستا، يوتيوب، فيسبوك، تويتر).")

if __name__ == "__main__":
    bot.infinity_polling()
