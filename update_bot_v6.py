# -*- coding: utf-8 -*-
"""
اسکریپت آپدیت خودکار Khan Trading Bot به نسخه 6.0 (Full Edition)
این فایل توکن‌ها و کلیدهای قبلی شما را از main.py برمی‌دارد و تمام ۵ ویژگی جدید را تزریق می‌کند.
"""
import os
import re

print("🔄 در حال ارتقای ربات Khan Trading به نسخه پیشرفته 6.0...")

if not os.path.exists("main.py"):
    print("❌ فایل main.py در این پوشه پیدا نشد! لطفاً فایل را داخل پوشه khan_trading_bot_v5 اجرا کنید.")
    exit(1)

with open("main.py", "r", encoding="utf-8", errors="ignore") as f:
    old_code = f.read()

# استخراج توکن تلگرام و کلید جمینای از فایل قبلی
bot_token = ""
gemini_key = ""

token_match = re.search(r'BOT_TOKEN\s*=\s*["\']([^"\']+)["\']', old_code)
if token_match:
    bot_token = token_match.group(1)

gemini_match = re.search(r'GEMINI_API_KEY\s*=\s*["\']([^"\']+)["\']', old_code)
if gemini_match:
    gemini_key = gemini_match.group(1)

if not bot_token:
    token_match = re.search(r'["\']([0-9]{8,10}:[a-zA-Z0-9_-]{35})["\']', old_code)
    if token_match:
        bot_token = token_match.group(1)

if not gemini_key:
    gemini_match = re.search(r'["\'](AIzaSy[a-zA-Z0-9_-]{33})["\']', old_code)
    if gemini_match:
        gemini_key = gemini_match.group(1)

print(f"✅ توکن تلگرام شناسایی شد: {bot_token[:10]}..." if bot_token else "⚠️ توکن تلگرام به صورت خودکار شناسایی نشد.")
print(f"✅ کلید جمینای شناسایی شد: {gemini_key[:10]}..." if gemini_key else "⚠️ کلید جمینای به صورت خودکار شناسایی نشد.")

# اگر فایل khan_bot_full.py کنارش بود از اون می‌خونه، در غیر این صورت کد جدید رو می‌نویسه
if os.path.exists("khan_bot_full.py"):
    with open("khan_bot_full.py", "r", encoding="utf-8") as f:
        new_template = f.read()
else:
    print("❌ فایل khan_bot_full.py یافت نشد.")
    exit(1)

# جایگزینی کلیدهای کاربر در فایل جدید
if bot_token:
    new_template = re.sub(r'BOT_TOKEN\s*=\s*os\.getenv\(["\']BOT_TOKEN["\'],\s*["\'][^"\']*["\']\)', f'BOT_TOKEN = os.getenv("BOT_TOKEN", "{bot_token}")', new_template)
if gemini_key:
    new_template = re.sub(r'GEMINI_API_KEY\s*=\s*os\.getenv\(["\']GEMINI_API_KEY["\'],\s*["\'][^"\']*["\']\)', f'GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "{gemini_key}")', new_template)

# پشتیبان‌گیری از نسخه قبلی
with open("main.py.bak", "w", encoding="utf-8") as f:
    f.write(old_code)
print("📦 نسخه پشتیبان در main.py.bak ذخیره شد.")

# نوشتن نسخه جدید در main.py
with open("main.py", "w", encoding="utf-8") as f:
    f.write(new_template)

print("=" * 60)
print("🚀 تبریک! ربات شما با موفقیت به نسخه 6.0 (Full Edition) ارتقا یافت.")
print("💎 ۵ ماژول جدید فعال شدند: Gemini Vision + Live Search + Memory + Lot Calc + SMC Persona")
print("⚡ اکنون می‌توانید با دستور python main.py ربات را اجرا کنید.")
print("=" * 60)
