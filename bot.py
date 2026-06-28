import os
import threading
import http.server
import socketserver
import telebot
import yt_dlp
import requests

# --- سيرفر وهمي لمنع البوت من النوم ---
class DummyHTTPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("البوت يعمل عبر السيرفرات الوسيطة!".encode('utf-8'))

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

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not check_subscription(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="اضغط هنا للاشتراك بالقناة 📢", url="https://t.me/iq_2a1")
        markup.add(btn)
        bot.reply_to(message, "⚠️ عذراً عزيزي، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت!", reply_markup=markup)
        return
        
    bot.reply_to(message, "👋 أهلاً بك! لقد تم تفعيل سيرفرات التحميل السحابية لتخطي الحظر. أرسل أي رابط الآن!")

# دالة للاتصال بالخوادم الوسيطة لتخطي حظر يوتيوب وانستغرام
def get_direct_url(video_url):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    data = {"url": video_url}
    try:
        response = requests.post("https://api.cobalt.tools/api/json", json=data, headers=headers, timeout=15)
        if response.status_code == 200:
            res = response.json()
            if 'url' in res:
                return res['url']
    except:
        pass
    return None

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
    
    if any(domain in url_lower for domain in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "facebook.com", "fb.watch", "x.com", "twitter.com"]):
        status_msg = bot.reply_to(message, "🚀 جاري التحميل عبر السيرفرات السحابية...")
        
        # 1. محاولة التحميل عبر الخادم الوسيط (لتجنب حظر Render)
        direct_url = get_direct_url(url)
        
        if direct_url:
            try:
                bot.send_video(message.chat.id, direct_url, reply_to_message_id=message.message_id)
                bot.delete_message(message.chat.id, status_msg.message_id)
                return
            except:
                pass # في حال فشل الإرسال، ننتقل للطريقة الثانية
        
        # 2. الطريقة البديلة (الاعتماد على الكوكيز الداخلي)
        bot.edit_message_text("جاري المحاولة بالطريقة البديلة...", message.chat.id, status_msg.message_id)
        ydl_opts = {
            'format': 'b[ext=mp4]/best', 
            'outtmpl': f'video_{message.chat.id}_%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cookies_path = os.path.join(current_dir, 'cookies.txt')
        if os.path.exists(cookies_path):
            ydl_opts['cookiefile'] = cookies_path
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                bot.edit_message_text("📥 اكتمل التحميل! جاري الإرسال...", message.chat.id, status_msg.message_id)
                
                with open(filename, 'rb') as video:
                    bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
                    
                if os.path.exists(filename):
                    os.remove(filename)
                bot.delete_message(message.chat.id, status_msg.message_id)
        except Exception as e:
            bot.edit_message_text("❌ عذراً، لا تزال المنصة تحظر التحميل. قد يكون الحساب خاصاً (Private) أو محمياً بشدة.", message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "⚠️ أرسل رابطاً صحيحاً من المنصات المعروفة.")

if __name__ == "__main__":
    bot.infinity_polling()
