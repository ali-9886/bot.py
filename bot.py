import os
import threading
import http.server
import socketserver
import telebot
import requests

# =====================================================================
# 🛡️ ميزة منع السبات لسيرفر Render
# =====================================================================
class AliveHTTPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("🤖 البوت يعمل ومضاد للحظر!".encode('utf-8'))

def run_alive_server():
    PORT = int(os.environ.get("PORT", 8080))
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), AliveHTTPServer) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=run_alive_server, daemon=True).start()

# =====================================================================
# ⚙️ إعدادات البوت والاشتراك
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
# 📥 الترحيب
# =====================================================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not check_subscription(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="اضغط هنا ونورنا بالقناة 🌸", url="https://t.me/iq_2a1")
        markup.add(btn)
        bot.reply_to(message, "هلا بيك يا غالي ❤️\nاشترك بقناتنا أولاً من الزر الجوا 👇 لتفعيل البوت.", reply_markup=markup)
        return
    bot.reply_to(message, "هلا بيك يا طيب نورت البوت! ✨\n\nدزلي أي رابط (تيك توك، انستا، يوتيوب، تويتر) وخلّي الباقي عليه! 🚀")

# =====================================================================
# 🔮 نظام التحميل عبر الـ API الخارجي (لتجاوز حظر Render)
# =====================================================================
@bot.message_handler(func=lambda message: True)
def handle_download(message):
    if not check_subscription(message.from_user.id):
        return

    url = message.text.strip()
    url_lower = url.lower()
    supported = ["tiktok.com", "instagram.com", "youtube.com", "youtu.be", "facebook.com", "x.com", "twitter.com"]
    
    if any(domain in url_lower for domain in supported):
        status_msg = bot.reply_to(message, "تدلل! جاري سحب المقطع بالسيرفرات البديلة 🚀...")
        
        # 1️⃣ المحاولة الأولى: سيرفر Cobalt الشامل (يسحب انستا، تيك توك، يوتيوب، وتويتر)
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            res = requests.post("https://api.cobalt.tools/api/json", json={"url": url}, headers=headers, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                if data.get("status") in ["redirect", "stream", "success"]:
                    video_url = data.get("url")
                    bot.send_video(message.chat.id, video_url, reply_to_message_id=message.message_id, caption="تم التحميل بنجاح! 🍿✨")
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    return
        except:
            pass # إذا فشل Cobalt ننتقل للطرق البديلة

        # 2️⃣ المحاولة الثانية (مخصصة لتيك توك فقط)
        if "tiktok.com" in url_lower:
            try:
                res = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10).json()
                if res and res.get('code') == 0:
                    video_url = res['data']['play']
                    bot.send_video(message.chat.id, video_url, reply_to_message_id=message.message_id, caption="تحميل موفق من تيك توك! 🎬✨")
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    return
            except: pass

        # 3️⃣ المحاولة الثالثة (الروابط المطورة المباشرة لإنستغرام وتويتر)
        if "instagram.com" in url_lower:
            clean_url = url.split("?")[0]
            proxy_url = clean_url.replace("instagram.com", "ddinstagram.com").replace("www.", "")
            bot.send_message(message.chat.id, f"🍿 **مقطع إنستغرام جاهز للمشاهدة:**\n\n{proxy_url}", reply_to_message_id=message.message_id)
            bot.delete_message(message.chat.id, status_msg.message_id)
            return
            
        elif "x.com" in url_lower or "twitter.com" in url_lower:
            proxy_url = url.replace("x.com", "fxtwitter.com").replace("twitter.com", "fxtwitter.com")
            bot.send_message(message.chat.id, f"🍿 **مقطع تويتر جاهز:**\n\n{proxy_url}", reply_to_message_id=message.message_id)
            bot.delete_message(message.chat.id, status_msg.message_id)
            return

        # 4️⃣ في حال فشل كل السيرفرات الخارجية
        bot.edit_message_text("أعتذر منك يا غالي 💔، يبدو أن المقطع خاص، أو أن سيرفرات السحب عليها ضغط حالياً.", message.chat.id, status_msg.message_id)
    
    else:
        bot.reply_to(message, "يا طيب 🥲، هذا الرابط غير مدعوم أو غير صحيح.")

# =====================================================================
# 🚀 تشغيل البوت
# =====================================================================
if __name__ == "__main__":
    try:
        bot.remove_webhook()
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"❌ خطأ: {e}")
