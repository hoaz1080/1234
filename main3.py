import os
import requests
from queue import Queue
from threading import Thread
from telegram.ext import Updater, MessageHandler, Filters

# =======================
TELEGRAM_BOT_TOKEN = "1664467711:AAEMVD7dLYYn7lpJC85vqV9ACxgTU9PuM-g"
EITA_BOT_TOKEN = "bot410579:ca343b5b-678a-4b57-a206-952bc371e5ea"
EITA_CHAT_ID = 10898011 
DOWNLOAD_DIR = "/home/hoaz/bot/"
MAX_WORKERS = 3  # تعداد پردازش همزمان
CHUNK_SIZE = 1024 * 1024  # 1MB
# =======================


link_queue = Queue()


def send_to_eita(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            f"https://eitaayar.ir/api/{EITA_BOT_TOKEN}/sendFile",
            files={"file": f},
            data={
                "chat_id": EITA_CHAT_ID,
                "title": os.path.basename(file_path),
                "caption": "File sent from bot"
            }
        )
    print("Eita API Response:", response.text)


def download_and_send(url):
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    local_filename = os.path.join(DOWNLOAD_DIR, url.split("/")[-1])

    
    with requests.get(url, stream=True) as r, open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    
    send_to_eita(local_filename)

    
    os.remove(local_filename)


def worker():
    while True:
        url, update = link_queue.get()
        try:
            update.message.reply_text(f"⏳ در حال دانلود و ارسال فایل: {url}")
            download_and_send(url)
            update.message.reply_text("✅ فایل به ایتا ارسال شد و از سرور حذف شد.")
        except Exception as e:
            update.message.reply_text(f"❌ خطا در پردازش فایل: {e}")
        finally:
            link_queue.task_done()


def handle_message(update, context):
    url = update.message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        update.message.reply_text("❌ لطفاً لینک معتبر ارسال کنید.")
        return

    
    link_queue.put((url, update))
    position = link_queue.qsize()
    if position > MAX_WORKERS:
        update.message.reply_text(f"⏳ لینک شما در صف قرار گرفت. موقعیت در صف: {position}")
    else:
        update.message.reply_text("⏳ لینک شما در حال پردازش است...")


def main():
    # ایجاد Worker Threads
    for _ in range(MAX_WORKERS):
        t = Thread(target=worker, daemon=True)
        t.start()

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
