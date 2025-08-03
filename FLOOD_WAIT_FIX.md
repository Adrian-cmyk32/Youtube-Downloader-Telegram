# راهنمای حل مشکل FloodWait در ربات تلگرام
# Telegram Bot FloodWait Fix Guide

## مشکل چیه؟ (What was the problem?)

مشکل **FloodWait** زمانی اتفاق می‌افته که ربات خیلی سریع درخواست‌های زیادی به API تلگرام ارسال کنه. تلگرام برای جلوگیری از اسپم و حفظ سرویس، محدودیت تعدادی درخواست در هر ثانیه داره.

**FloodWait** error occurs when the bot sends too many requests to Telegram's API too quickly. Telegram has rate limits to prevent spam and maintain service quality.

## راه‌حل‌های پیاده‌شده (Implemented Solutions)

### 1. مدیریت خطاهای FloodWait (FloodWait Error Handling)
```python
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
                        time.sleep(delay)
                        continue
```

### 2. توابع ایمن برای API (Safe API Functions)
- `safe_send_message()` - ارسال ایمن پیام
- `safe_delete_message()` - حذف ایمن پیام  
- `safe_send_video()` - ارسال ایمن ویدیو
- `safe_send_audio()` - ارسال ایمن فایل صوتی

### 3. تأخیر بین درخواست‌ها (Delays Between Requests)
```python
time.sleep(0.5)  # تأخیر کوتاه
time.sleep(1)    # تأخیر متوسط
```

### 4. مدیریت بهتر حذف پیام‌ها (Better Message Deletion)
```python
if status_message:
    safe_delete_message(call.message.chat.id, status_message.message_id)
```

### 5. سیستم تلاش مجدد (Retry System)
- حداکثر 3 بار تلاش مجدد
- تأخیر تصاعدی: 1، 2، 4 ثانیه
- لاگ کردن خطاها

## تغییرات اعمال شده (Applied Changes)

### در فایل `telegram_bot.py`:
1. ✅ اضافه شدن `import logging` و `ApiTelegramException`
2. ✅ تابع `handle_flood_wait()` برای مدیریت خطاها
3. ✅ توابع ایمن برای تمام عملیات API
4. ✅ تأخیر مناسب بین پیام‌ها
5. ✅ بهبود مدیریت استثناها
6. ✅ سیستم راه‌اندازی مجدد خودکار

### در فایل `requirements.txt`:
- ✅ به‌روزرسانی `pyTelegramBotAPI` به نسخه `4.18.0`

## نحوه استفاده (How to Use)

### 1. به‌روزرسانی وابستگی‌ها
```bash
./update_requirements.sh
```

یا به صورت دستی:
```bash
pip install -r requirements.txt
```

### 2. اجرای ربات
```bash
python telegram_bot.py
```

## مزایای این راه‌حل (Benefits)

✅ **پایداری بیشتر**: ربات دیگه به خاطر FloodWait کرش نمی‌کنه

✅ **عملکرد بهتر**: تأخیرهای مناسب برای کاربران

✅ **لاگ مفصل**: ردیابی آسان‌تر مشکلات

✅ **راه‌اندازی خودکار**: ربات خودش دوباره راه می‌افته

✅ **سازگاری بهتر**: با آخرین نسخه کتابخانه‌ها

## نکات مهم (Important Notes)

⚠️ **توکن ربات**: فراموش نکنید توکن ربات خودتون رو در `telegram_bot.py` قرار بدید

⚠️ **ID کانال‌ها**: ID کانال‌هاتون رو به‌روزرسانی کنید

⚠️ **مجوز فایل**: اطمینان حاصل کنید که `update_requirements.sh` قابل اجرا باشه

## بررسی عملکرد (Performance Monitoring)

برای بررسی لاگ‌ها:
```bash
python telegram_bot.py 2>&1 | tee bot.log
```

## پشتیبانی (Support)

اگر مشکلی پیش اومد:
1. لاگ‌ها رو بررسی کنید
2. اتصال اینترنت رو چک کنید  
3. توکن ربات رو بررسی کنید
4. نسخه Python (باید 3.8+ باشه)

---

**نتیجه**: حالا ربات شما باید بدون مشکل FloodWait کار کنه! 🎉

**Result**: Your bot should now work without FloodWait issues! 🎉