import os
import requests
from telegram.ext import Updater, MessageHandler, Filters

# توکن‌ها
TELEGRAM_BOT_TOKEN = "1664467711:AAEMVD7dLYYn7lpJC85vqV9ACxgTU9PuM-g"
EITA_BOT_TOKEN = "bot410579:ca343b5b-678a-4b57-a206-952bc371e5ea"
EITA_CHAT_ID = "hoaz1234"

# تابع برای دانلود و ارسال
def download_and_send(url):
    local_filename = url.split("/")[-1]
    
    # دانلود فایل
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    # ارسال فایل به ایتا
    with open(local_filename, 'rb') as f:
        requests.post(
            f"https://eitaayar.ir/bot{EITA_BOT_TOKEN}/sendDocument",
            data={"chat_id": EITA_CHAT_ID},
            files={"document": f}
        )
    
    # حذف فایل
    os.remove(local_filename)

# هندلر برای پیام‌های تلگرام
def handle_message(update, context):
    url = update.message.text.strip()
    if url.startswith("http://") or url.startswith("https://"):
        update.message.reply_text("⏳ در حال دانلود و ارسال به ایتا ...")
        try:
            download_and_send(url)
            update.message.reply_text("✅ فایل به ایتا ارسال شد و از سرور حذف گردید.")
        except Exception as e:
            update.message.reply_text(f"❌ خطا: {e}")
    else:
        update.message.reply_text("لطفاً لینک معتبر ارسال کنید.")

# اجرای ربات
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
