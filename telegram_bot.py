import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException
from pytube import YouTube
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import time
import requests
import sqlite3
import logging

# تنظیم لاگ
logging.basicConfig(level=logging.INFO)


conn = sqlite3.connect('users.db')
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (user_id INTEGER PRIMARY KEY)''')
                  
cursor.execute('''ALTER TABLE users ADD COLUMN is_blocked INTEGER DEFAULT 0''')

conn.commit()
conn.close()

# تابع مدیریت خطاهای FloodWait
def handle_flood_wait(func):
    def wrapper(*args, **kwargs):
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except ApiTelegramException as e:
                if "Too Many Requests" in str(e) or "Flood control exceeded" in str(e):
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        logging.warning(f"FloodWait detected, waiting {delay} seconds before retry {attempt + 1}")
                        time.sleep(delay)
                        continue
                    else:
                        logging.error("Max retries exceeded for FloodWait")
                        raise
                else:
                    raise
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                raise
        
        return None
    return wrapper

# تابع ایمن برای ارسال پیام
@handle_flood_wait
def safe_send_message(chat_id, text, **kwargs):
    return bot.send_message(chat_id, text, **kwargs)

# تابع ایمن برای حذف پیام
@handle_flood_wait
def safe_delete_message(chat_id, message_id):
    try:
        return bot.delete_message(chat_id, message_id)
    except Exception as e:
        logging.warning(f"Could not delete message: {e}")

# تابع ایمن برای ارسال ویدیو
@handle_flood_wait
def safe_send_video(chat_id, video, **kwargs):
    return bot.send_video(chat_id, video, **kwargs)

# تابع ایمن برای ارسال صوت
@handle_flood_wait
def safe_send_audio(chat_id, audio, **kwargs):
    return bot.send_audio(chat_id, audio, **kwargs)

token = 'Your-Bot-Token'

channel_id = -1243423432 # ایدی عددی کانالی که قرا است رربات ممبر های عضو شده یا نشده را چک کند 
channel_join = -123456789  # ایدی عددی کانالی که ربات وقتی کاربری ربات را استارت کرد یک اعلان در کانال ارسال کند


bot = telebot.TeleBot(token)

# تابع بررسی وجود کاربر در دیتابیس
def is_user_exist(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# تابع افزودن کاربر به دیتابیس
def add_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    
    
@bot.message_handler(commands=['start'])
def handle_start(message):
    # بررسی عضویت کاربر در کانال
    user_id = message.from_user.id
    is_member = check_membership(user_id, channel_id)
    
    if is_member:
        if not is_user_exist(user_id):
            add_user(user_id)
            # اضافه کردن تأخیر برای جلوگیری از FloodWait
            time.sleep(0.5)
            
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
        button1 = KeyboardButton('دانلود از یوتیوب')
        button2 = KeyboardButton('پشتیبانی')
        keyboard.add(button1, button2)
        
        # استفاده از تابع ایمن برای ارسال پیام
        safe_send_message(message.chat.id, f""" سلام  {message.from_user.first_name}  به ربات یوتیوب دانلودر خوش آمدی♥️

    لینک ویدیوی یوتیوبتو برام بفرس و سریع تحویل بگیر ⚡️

    🦧 برای شروع یکی از گزینه های زیر رو انتخاب کن :""", reply_markup=keyboard)
        
        # تأخیر قبل از ارسال پیام به کانال
        time.sleep(1)
        safe_send_message(channel_join, f"کاربر جدید با نام {message.from_user.first_name} عضو ربات شد.")

    else:
        safe_send_message(message.chat.id, """کاربر گرامی لطفا برای استفاده از ربات ، ابتدا در کانال زیر عضو شوید 👀 
🆔 @newpacks

و سپس دوباره دستور   /start را ارسال کنید. """)
        
        


    
    
# بررسی عضویت کاربر در کانال
def check_membership(user_id, channel_id):
    try:
        member = bot.get_chat_member(channel_id, user_id)
        if member.status == 'left':
            return False
        else:
            return True
        
    except telebot.apihelper.ApiException as e:
        if e.result_json['description'] == 'Bad Request : chat not found':
         return False
    
  
# تابع ارسال پیام به تمام کاربران
        #این تابع به دلیل استفاده خیلی کم به کامنت تبدیل شده است برای استفاده فقط کافی است تا از حالت کامنت در بیاید

"""def send_message_to_all_users(message_text):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE is_blocked = 0")  # فقط کاربرانی که بلاک نشده‌اند
    user_ids = cursor.fetchall()
    conn.close()
    
    for user_id in user_ids:
        try:
            # بررسی عضویت کاربر در کانال
            member = bot.get_chat_member(channel_id, user_id[0])
            if member.status != 'left':
                bot.send_message(user_id[0], message_text)
        except Exception as e:
            print(f"Error occurred while sending message to user {user_id[0]}: {e}")

# مثال استفاده از تابع
send_message_to_all_users("ربات آپدیت شد✅\n\n لطفا برای استفاده دوباره ربات را /start کنید.")
"""

@bot.message_handler(func=lambda message: message.text == "دانلود از یوتیوب")
def handle_download_button(message):
    is_member = check_membership(message.from_user.id, channel_id)
    if is_member:
        safe_send_message(message.chat.id, "لطفاً لینک ویدیوی YouTube را ارسال کنید.📬", reply_to_message_id=message.message_id)
    else:
        safe_send_message(message.chat.id, 'شما باید عضو کانال ما باشید تا بتوانید از این قابلیت استفاده کنید.')
        
        

@bot.message_handler(func=lambda message: message.text == "پشتیبانی")
def handle_supp_button(message):   
    safe_send_message(message.chat.id,'فعلا برقراری ارتباط با پشتیبانی مقدور نیست \n بعدا امتحان کنید😁')
        
# 
@bot.message_handler(func=lambda message: True)
def handle_video_link(message):
    try:
 
        video_url = message.text
        youtube = YouTube(video_url)
        

        # ایجاد گزینه‌های انتخاب کیفیت ویدیو
        keyboard = types.InlineKeyboardMarkup(row_width=2)
    
        status_message = safe_send_message(message.chat.id,'در حال جستجوی کیفیت های موجود برای دانلود...⏳')
        time.sleep(0.5)  # تأخیر برای جلوگیری از FloodWait
        
        for stream in youtube.streams.filter(file_extension='mp4', progressive=True) :
                button_text = f" 🎬  {stream.resolution} - {stream.filesize / (1024 * 1024):.1f} MB"
                button = types.InlineKeyboardButton(text=button_text, callback_data=stream.itag)
                keyboard.add(button)
                
        for stream in youtube.streams.filter(file_extension='mp4', resolution='480p'):
            button_text = f"🎬  {stream.resolution} - {stream.filesize / (1024 * 1024):.1f} MB"
            button = types.InlineKeyboardButton(text=button_text, callback_data=stream.itag)
            keyboard.add(button)
            
            
        button_audio_128 = types.InlineKeyboardButton(text=" 128kbps  🎧 ", callback_data="audio_128")
        button_audio_320 = types.InlineKeyboardButton(text=" 320kbps  🎧", callback_data="audio_320")
        keyboard.add(button_audio_128, button_audio_320)    
                
        if status_message:
            safe_delete_message(message.chat.id, status_message.message_id)
        
        global qual_mssg
        # ارسال گزینه‌های انتخاب کیفیت به کاربر
        qual_mssg = safe_send_message(message.chat.id, 'لطفا کیفیت ویدیو رو انتخاب کن :', reply_markup=keyboard)
        
        # ذخیره لینک ویدیو
        bot.video_url = video_url

    except Exception as e:
        logging.error(f"Error in video handler: {e}")
        safe_send_message(message.chat.id, 'خطا در بارگیری ویدیو ، یک لینک معتبر ارسال کن .')

# پاسخ به انتخاب کیفیت ویدیو
@bot.callback_query_handler(func=lambda call: True)
def handle_quality_selection(call):
    try:
        video_url = bot.video_url
        youtube = YouTube(video_url)

        if call.data == "audio_128":
            # دانلود ویدیو با کیفیت انتخاب شده
            video = youtube.streams.get_by_itag(140)
            safe_delete_message(call.message.chat.id, qual_mssg.message_id)
            time.sleep(0.5)  # تأخیر قبل از ارسال پیام بعدی
            
            status_message = safe_send_message(call.message.chat.id, 'در حال دانلود فایل صوتی...')
            bot.send_chat_action(call.message.chat.id, 'upload_audio')

            # دانلود فایل صوتی
            audio_file = video.download()
            if status_message:
                safe_delete_message(call.message.chat.id, status_message.message_id)
            time.sleep(0.5)
            
            # پاکسازی فایل موقت
            if os.path.exists(audio_file):
                caption = f"عنوان : {youtube.title}\n ناشر : {youtube.author}\n مدت زمان : {youtube.length} ثانیه\n @newpacks"
                upload_statues = safe_send_message(call.message.chat.id, 'در حال آپلود فایل صوتی...')
                time.sleep(1)  # کاهش تأخیر
                safe_send_audio(call.message.chat.id, open(audio_file, 'rb'), caption=caption)
                if upload_statues:
                    safe_delete_message(call.message.chat.id, upload_statues.message_id)
                time.sleep(0.5)
                safe_send_message(call.message.chat.id, 'فایل صوتی ارسال شد✅ ')
                os.remove(audio_file)  # حذف فایل موقت پس از ارسال
            else:
                safe_send_message(call.message.chat.id, 'خطا در دانلود فایل صوتی.')
        
        elif call.data == "audio_320":
            # دانلود ویدیو با کیفیت انتخاب شده
            video = youtube.streams.get_by_itag(251)
            safe_delete_message(call.message.chat.id, qual_mssg.message_id)
            time.sleep(0.5)  # تأخیر قبل از ارسال پیام بعدی
            
            status_message = safe_send_message(call.message.chat.id, 'در حال دانلود فایل صوتی...')
            bot.send_chat_action(call.message.chat.id, 'upload_audio')

            # دانلود فایل صوتی
            audio_file = video.download()
            if status_message:
                safe_delete_message(call.message.chat.id, status_message.message_id)
            time.sleep(0.5)
            
            # پاکسازی فایل موقت
            if os.path.exists(audio_file):
                caption = f"عنوان : {youtube.title}\n ناشر : {youtube.author}\n مدت زمان : {youtube.length} ثانیه\n @newpacks"
                upload_statues = safe_send_message(call.message.chat.id, 'در حال آپلود فایل صوتی...')
                time.sleep(1)  # کاهش تأخیر
                safe_send_audio(call.message.chat.id, open(audio_file, 'rb'), caption=caption)
                if upload_statues:
                    safe_delete_message(call.message.chat.id, upload_statues.message_id)
                time.sleep(0.5)
                safe_send_message(call.message.chat.id, 'فایل صوتی ارسال شد✅ ')
                os.remove(audio_file)  # حذف فایل موقت پس از ارسال
            else:
                safe_send_message(call.message.chat.id, 'خطا در دانلود فایل صوتی.')
        
        else:
            
            # چک کردن اندازه فایل برای ویدیوهای با حجم بیشتر از 50 مگابایت
            video = youtube.streams.get_by_itag(call.data)
            file_size = video.filesize
            
            if file_size > 50 * 1024 * 1024:  # بررسی اندازه فایل (بیشتر از 50 مگابایت)
                safe_send_message(call.message.chat.id, """ متاسفانه با توجه به محدودیت های تلگرام نمیتونیم ویدیو هایی با حجم بیشتر از 50 مگابایت رو برات ارسال کنیم 😕

در تلاشیم که این محدودیت را رفع کنیم و به زودی به شما خبر میدیم ❤️
""") 
                return  # پایان فرآیند در صورت بیشتر بودن حجم فایل
            # در غیر این صورت، دانلود ویدیو با کیفیت انتخاب شده
            video = youtube.streams.get_by_itag(call.data)
            safe_delete_message(call.message.chat.id, qual_mssg.message_id)
            time.sleep(0.5)  # تأخیر قبل از ارسال پیام بعدی
            
            status_message = safe_send_message(call.message.chat.id, 'در حال دانلود ویدیو...')
            bot.send_chat_action(call.message.chat.id, 'upload_video')

            # دانلود فایل ویدیو
            video_file = video.download()
            
            if status_message:
                safe_delete_message(call.message.chat.id, status_message.message_id)
            time.sleep(0.5)

            # پاکسازی فایل موقت
            if os.path.exists(video_file):
                caption = f"عنوان : {youtube.title}\n ناشر : {youtube.author}\n مدت زمان : {youtube.length} ثانیه\n @newpacks"
                upload_statues = safe_send_message(call.message.chat.id, 'در حال آپلود ویدیو...')
                time.sleep(1)  # کاهش تأخیر
                safe_send_video(call.message.chat.id, open(video_file, 'rb'), caption=caption,supports_streaming=True)
                if upload_statues:
                    safe_delete_message(call.message.chat.id, upload_statues.message_id)
                time.sleep(0.5)
                safe_send_message(call.message.chat.id, 'ویدیو ارسال شد✅ ')
                os.remove(video_file)  # حذف فایل موقت پس از ارسال
            else:
                safe_send_message(call.message.chat.id, 'خطا در دانلود ویدیو.')
 
    except Exception as e:
        logging.error(f"Error in callback handler: {e}")
        safe_send_message(call.message.chat.id, 'خطا در دانلود.')
           

# شروع ربات با مدیریت خطا
if __name__ == "__main__":
    while True:
        try:
            logging.info("Starting bot...")
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            logging.error(f"Bot polling error: {e}")
            logging.info("Restarting bot in 5 seconds...")
            time.sleep(5)
