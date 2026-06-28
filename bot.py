import os
import threading
import http.server
import socketserver
import telebot
import yt_dlp
import requests
import random

# --- سيرفر وهمي مدمج للحفاظ على استمرارية البوت عبر UptimeRobot ---
class DummyHTTPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("بوت البروكسي الديناميكي الذكي يعمل بنجاح!".encode('utf-8'))

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

# 🌐 دالة ذكية لجلب بروكسيات حية ونظيفة مجاناً وتحديثها تلقائياً لتخطي حظر إنستغرام
def fetch_live_proxies():
    proxy_urls = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
        "https://www.proxy-list.download/api/v1/get?type=https"
    ]
    discovered = []
    for url in proxy_urls:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                extracted = [p.strip() for p in res.text.split("\n") if p.strip()]
                discovered.extend(extracted)
        except:
            continue
    return list(set(discovered))

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not check_subscription(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="اضغط هنا للاشتراك بالقناة 📢", url="https://t.me/iq_2a1")
        markup.add(btn)
        bot.reply_to(message, "⚠️ عذراً عزيزي، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت!", reply_markup=markup)
        return
    bot.reply_to(message, "🚀 أهلاً بك في النسخة الفولاذية! تم دمج نظام كسر الحظر الديناميكي (Dynamic Proxy) لمنع توقف إنستغرام ويوتيوب نهائياً.")

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
        status_msg = bot.reply_to(message, "⚡ جاري تشغيل نفق البروكسي السري وسحب المقطع الآن...")
        
        # إعدادات التحميل الأساسية لـ yt-dlp
        ydl_opts = {
            'format': 'b[ext=mp4]/best', 
            'outtmpl': f'video_{message.chat.id}_%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            }
        }

        # محاولة التحميل بالطريقة العادية أولاً (إذا كان السيرفر غير محظور في تلك اللحظة)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                dl_filename = ydl.prepare_filename(info)
                with open(dl_filename, 'rb') as video:
                    bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
                if os.path.exists(dl_filename): os.remove(dl_filename)
                bot.delete_message(message.chat.id, status_msg.message_id)
                return
        except Exception:
            pass

        # 🔥 إذا فشل التحميل العادي (بسبب الحظر)، نقوم بتفعيل خطة البروكسي الديناميكي فوراً
        bot.edit_message_text("🔄 تم كشف حظر من إنستغرام/يوتيوب.. جاري تدوير البروكسيات وتخطي الحظر تلقائياً...", message.chat.id, status_msg.message_id)
        
        live_proxies = fetch_live_proxies()
        random.shuffle(live_proxies) # خلط البروكسيات لضمان العشوائية والنجاح
        
        success = False
        # تجربة أفضل 8 بروكسيات حية تم سحبها حديثاً
        for proxy in live_proxies[:8]:
            try:
                formatted_proxy = f"http://{proxy}"
                ydl_opts['proxy'] = formatted_proxy
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    dl_filename = ydl.prepare_filename(info)
                    
                    with open(dl_filename, 'rb') as video:
                        bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
                        
                    if os.path.exists(dl_filename): os.remove(dl_filename)
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    success = True
                    break
            except Exception:
                continue # إذا فشل بروكسي ينتقل للذي بعده فوراً خلال أجزاء من الثانية
                
        if not success:
            # محاولة أخيرة عبر الهندسة العكسية لروابط إنستغرام المباشرة
            if "instagram.com" in url_lower:
                try:
                    proxy_insta = url.replace("instagram.com", "ddinstagram.com").replace("www.", "")
                    bot.send_video(message.chat.id, proxy_insta, reply_to_message_id=message.message_id)
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    return
                except:
                    pass
            bot.edit_message_text("❌ جميع البروكسيات العالمية مضغوطة حالياً. يرجى إعادة إرسال الرابط بعد ثوانٍ قليلة لتوليد حزمة بروكسيات جديدة.", message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "⚠️ أرسل رابطاً صحيحاً ومدعوماً.")

if __name__ == "__main__":
    bot.infinity_polling()
