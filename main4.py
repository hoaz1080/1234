import os
import time
import requests
import queue
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from telegram.ext import Updater, MessageHandler, Filters

# ================== تنظیمات ==================
TELEGRAM_BOT_TOKEN = "1664467711:AAEMVD7dLYYn7lpJC85vqV9ACxgTU9PuM-g"
CHAT_URL = "https://web.eitaa.com/#@myhoaz"  # لینک گروه/چت ایتا
DOWNLOAD_DIR = "/home/hoaz/bot"     # پوشه ذخیره موقت فایل‌ها
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"     # مسیر chromedriver

# ================== صف دانلود ==================
task_queue = queue.Queue()
processing = False

def download_file(url):
    """دانلود فایل از لینک"""
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    local_filename = os.path.join(DOWNLOAD_DIR, url.split("/")[-1])
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return local_filename

def send_to_eitaa(file_path):
    
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    driver.get("https://web.eitaa.com/")
    time.sleep(10)
    input("⚠️ وارد اکانت شو، بعد Enter بزن...")

    driver.get(CHAT_URL)
    time.sleep(5)

    attach_btn = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
    attach_btn.send_keys(file_path)

    time.sleep(3)
    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER).perform()

    print("✅ فایل ارسال شد")
    time.sleep(10)
    driver.quit()

    os.remove(file_path)

def worker():
    """پردازش صف فایل‌ها"""
    global processing
    while True:
        url, update = task_queue.get()
        processing = True
        try:
            update.message.reply_text("⏳ در حال دانلود و آپلود فایل...")
            file_path = download_file(url)
            send_to_eitaa(file_path)
            update.message.reply_text("✅ فایل با موفقیت به ایتا ارسال شد.")
        except Exception as e:
            update.message.reply_text(f"❌ خطا: {e}")
        finally:
            processing = False
            task_queue.task_done()

def handle_message(update, context):
    """دریافت لینک از تلگرام"""
    url = update.message.text.strip()
    if url.startswith("http://") or url.startswith("https://"):
        if processing:
            update.message.reply_text("⚠️ یک فایل دیگر در حال پردازش است. لینک شما در صف قرار گرفت.")
        else:
            update.message.reply_text("⏳ فایل شما در حال پردازش است...")
        task_queue.put((url, update))
    else:
        update.message.reply_text("لطفاً یک لینک معتبر ارسال کنید.")

def main():
    
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    
    threading.Thread(target=worker, daemon=True).start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
