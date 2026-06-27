import os
import telebot
from yt_dlp import YoutubeDL

# ⚠️ ضع توكن البوت الخاص بك هنا بين علامتي التنصيص
BOT_TOKEN = "8499856454:AAHB49UPTI7Q4sF0OyMr-GhBPOIVk9aBRRo"

bot = telebot.TeleBot(BOT_TOKEN)

# التأكد من وجود مجلد مؤقت للتحميلات
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_msg = (
        "👋 أهلاً بك في بوت التحميل العالمي المستمر!\n\n"
        "📥 أرسل لي أي رابط فيديو أو موسيقى من المنصات التالية:\n"
        "🔹 TikTok  🔹 Instagram  🔹 YouTube  🔹 Facebook\n\n"
        "🚀 يعمل البوت تلقائياً 24/7 ومستعد لخدمتك أنت وأصدقائك في أي وقت!"
    )
    bot.reply_to(message, welcome_msg)

@bot.message_handler(func=lambda message: True)
def process_download(message):
    url = message.text
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ عذراً، يجب أن ترسل رابطاً صحيحاً يبدأ بـ http أو https.")
        return

    # رسالة مؤقتة تظهر للمستخدم أثناء المعالجة
    status = bot.reply_to(message, "⏳ جاري فحص الرابط وبدء التحميل من السيرفر...")

    # إعدادات تحميل ذكية متوافقة مع سيرفر Render ومحددة بـ 45 ميجا لتفادي قيود تليجرام
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'max_filesize': 45 * 1024 * 1024,
        'quiet': True,
        'no_warnings': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'فيديو محمل')

        bot.edit_message_text("🚀 اكتمل التحميل من المنصة! جاري رفع الفيديو إليك الآن...", chat_id=message.chat.id, message_id=status.message_id)
        
        # إرسال الفيديو النهائي للمستخدم أو أي شخص يستخدم البوت
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=f"🎬 {title}\n\n✨ تم التحميل بنجاح عبر السيرفر المستمر.")
        
        # حذف الملف فوراً من السيرفر لتوفير المساحة وضمان استمرار الخدمة مجاناً
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(chat_id=message.chat.id, message_id=status.message_id)

    except Exception as e:
        err = str(e)
        if "max_filesize" in err or "too large" in err:
            bot.edit_message_text("❌ حجم الفيديو كبير جداً! السيرفر المجاني يدعم الملفات حتى 45 ميجابايت فقط لضمان السرعة.", chat_id=message.chat.id, message_id=status.message_id)
        else:
            bot.edit_message_text("❌ حدث خطأ أثناء معالجة الرابط. تأكد أن الحساب عام (وليس خاصاً) أو جرب مجدداً لاحقاً.", chat_id=message.chat.id, message_id=status.message_id)
        
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

# تنظيف أي اتصالات قديمة أو معلقة فوراً عند بدء التشغيل لمنع خطأ 409 الشهير
try:
    bot.remove_webhook()
    print("🧹 تم تنظيف الاتصالات السابقة وجعل البوت جاهزاً بشكل نقي.")
except:
    pass

print("🚀 البوت انطلق بنجاح ويعمل الآن أونلاين على مدار الساعة...")
bot.infinity_polling(timeout=20, long_polling_timeout=10)
