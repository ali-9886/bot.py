import os
import threading
import http.server
import socketserver
import telebot
import yt_dlp

# --- سيرفر وهمي لمنع البوت من النوم ---
class DummyHTTPServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("البوت يعمل مع تقنية التخفي المتقدمة!".encode('utf-8'))

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
        
    bot.reply_to(message, "👋 أهلاً بك! لقد تم تحديث نظام التحميل وتخطي الحظر. أرسل لي أي رابط الآن.")

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
        status_msg = bot.reply_to(message, "🚀 جاري فك التشفير والتحميل (قد يستغرق الأمر لحظات)...")
        
        # إعدادات متقدمة جداً للتخفي وخداع سيرفرات يوتيوب وانستغرام
        ydl_opts = {
            'format': 'b[ext=mp4]/best', 
            'outtmpl': f'video_{message.chat.id}_%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'extractor_args': {
                'youtube': ['player_client=android,ios,web'] # إيهام يوتيوب أن الطلب من هاتف
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
            }
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
            print(f"Error: {str(e)}")
            bot.edit_message_text("❌ عذراً، حماية المنصة تمنع التحميل حالياً من هذا الرابط. جرب رابطاً آخر.", message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "⚠️ أرسل رابطاً صحيحاً من المنصات المعروفة.")

if __name__ == "__main__":
    bot.infinity_polling()
