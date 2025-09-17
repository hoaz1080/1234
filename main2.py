import os
import requests
import time
from telegram.ext import Updater, MessageHandler, Filters

# =======================
# توکن‌ها و آیدی‌ها
TELEGRAM_BOT_TOKEN = "1664467711:AAEMVD7dLYYn7lpJC85vqV9ACxgTU9PuM-g"
EITA_BOT_TOKEN = "bot410579:ca343b5b-678a-4b57-a206-952bc371e5ea"
EITA_CHAT_ID = 10898011  # حتماً عددی باشه، برای گروه منفی است
# =======================

# قفل برای جلوگیری از همزمانی
is_busy = False

# تابع برای ارسال فایل به ایتا
def send_to_eita(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            f"https://eitaayar.ir/api/{EITA_BOT_TOKEN}/sendFile",
            files={"file": f},
            data={
                "chat_id": EITA_CHAT_ID,
                "title": os.path.basename(file_path),
                "caption": "File sent from bot",
            }
        )
    print("Eita API Response:", response.text)

# دانلود و ارسال فایل
def download_and_send(url):
    local_filename = "/home/hoaz/bot/" + url.split("/")[-1]
    # دانلود فایل
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    # ارسال به ایتا
    send_to_eita(local_filename)
    # حذف فایل
    os.remove(local_filename)

# هندلر پیام‌های تلگرام
def handle_message(update, context):
    global is_busy
    url = update.message.text.strip()

    if not (url.startswith("http://") or url.startswith("https://")):
        update.message.reply_text("❌ لطفاً لینک معتبر ارسال کنید.")
        return

    if is_busy:
        update.message.reply_text("⚠️ سرور در حال پردازش یک فایل است. لطفاً بعداً تلاش کنید.")
        return

    is_busy = True
    update.message.reply_text("⏳ فایل شما در حال دانلود و ارسال به ایتا است...")

    try:
        download_and_send(url)
        update.message.reply_text("✅ فایل به ایتا ارسال شد و از سرور حذف گردید.")
    except Exception as e:
        update.message.reply_text(f"❌ خطا: {e}")
    finally:
        is_busy = False

# اجرای ربات
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
