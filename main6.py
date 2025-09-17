import os
import json
import time
import queue
import threading
import tempfile
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from telegram import Update
from telegram.ext import Updater, MessageHandler, CallbackContext, Filters

# ---------------- CONFIG ----------------
TELEGRAM_BOT_TOKEN = "1664467711:AAEMVD7dLYYn7lpJC85vqV9ACxgTU9PuM-g"
CHAT_ID = "10898011"  # آی‌دی چت یا کانال خودت
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
CHROME_PATH = "/snap/bin/chromium"  # مسیر chromium روی اوبونتو
COOKIES_FILE = "cookies.json"
EITA_URL = "https://web.eitaa.com/#@myhoaz"
DOWNLOAD_CHUNK = 1024*1024  # 1MB
# ---------------------------------------

# صف لینک‌ها
link_queue = queue.Queue()
is_processing = False

# تابع دانلود فایل
def download_file(url):
    local_filename = url.split("/")[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=DOWNLOAD_CHUNK):
                f.write(chunk)
    return local_filename

# تابع آپلود فایل در Eita با Selenium Headless
def upload_to_eita(local_file):
    chrome_options = Options()
    chrome_options.binary_location = CHROME_PATH
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")

    # مسیر یکتا برای پروفایل هر اجرا
    tmp_profile = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={tmp_profile}")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # ورود با کوکی‌ها
    driver.get(EITA_URL)
    time.sleep(3)
    with open(COOKIES_FILE, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(3)

    # پیدا کردن المان آپلود و ارسال فایل
    # ⚠️ توجه: این قسمت باید بر اساس structure واقعی سایت Eita اصلاح شود
    upload_input = driver.find_element("xpath", '//input[@type="file"]')
    upload_input.send_keys(os.path.abspath(local_file))
    time.sleep(5)  # زمان برای آپلود

    driver.quit()
    os.remove(local_file)
    print(f"✅ فایل {local_file} آپلود شد و حذف گردید.")

# پردازش لینک‌ها
def process_queue():
    global is_processing
    while True:
        url, chat_id, context = link_queue.get()
        is_processing = True
        try:
            context.bot.send_message(chat_id=chat_id, text="⏳ در حال دانلود و آپلود به Eita...")
            local_file = download_file(url)
            upload_to_eita(local_file)
            context.bot.send_message(chat_id=chat_id, text="✅ فایل به Eita ارسال شد!")
        except Exception as e:
            context.bot.send_message(chat_id=chat_id, text=f"❌ خطا: {e}")
        is_processing = False
        link_queue.task_done()

# هندلر پیام‌ها
def handle_message(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    chat_id = update.message.chat_id
    if url.startswith("http://") or url.startswith("https://"):
        if is_processing:
            update.message.reply_text("⏳ سرور در حال پردازش لینک قبلی است، لطفاً صبر کنید...")
        else:
            link_queue.put((url, chat_id, context))
            update.message.reply_text("✅ لینک شما در صف پردازش قرار گرفت.")
    else:
        update.message.reply_text("لطفاً یک لینک معتبر ارسال کنید.")

# اجرای ربات
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # شروع پردازش لینک‌ها در یک thread جدا
    threading.Thread(target=process_queue, daemon=True).start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
