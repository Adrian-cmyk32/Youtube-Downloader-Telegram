#!/bin/bash

echo "به‌روزرسانی وابستگی‌های پروژه..."
echo "Updating project dependencies..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "ایجاد محیط مجازی..."
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "فعال‌سازی محیط مجازی..."
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install/update requirements
echo "نصب/به‌روزرسانی وابستگی‌ها..."
echo "Installing/updating dependencies..."
pip install -r requirements.txt

echo "به‌روزرسانی کامل شد!"
echo "Update completed!"

echo ""
echo "برای اجرای ربات از دستور زیر استفاده کنید:"
echo "To run the bot, use the following command:"
echo "source venv/bin/activate && python telegram_bot.py"