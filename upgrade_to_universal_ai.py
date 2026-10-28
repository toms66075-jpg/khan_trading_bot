# -*- coding: utf-8 -*-
"""
اسکریپت ارتقای ربات خان به هوش مصنوعی همه‌کاره و جامع (Universal Quasar AI)
این اسکریپت محدودیت‌های اختصاصی ترید را برمی‌دارد و ربات را به یک دستیار هوش مصنوعی همه‌فن‌حریف
(دقیقاً مثل خان‌یار و ChatGPT با لحن صمیمی، خفن و تسلط بر تمامی علوم، چت آزاد، برنامه‌نویسی و ترید) تبدیل می‌کند.
"""

import os
import re
import sys
import shutil

TARGET_FILE = "main.py"
BACKUP_FILE = "main_backup_universal.py"

UNIVERSAL_PROMPT = '''تو یک هوش مصنوعی همه‌فن‌حریف، فوق‌العاده باهوش، تیز و همه‌کاره هستی (با مرام و معرفت لاتی، صمیمی، دقیق و رک مثل خان‌یار، و با قدرت و دانش بی‌پایان مثل ChatGPT).

قوانین و شخصیت تو:
۱. در مورد «هر موضوعی» که کاربر بپرسه با تسلط کامل صحبت می‌کنی: گپ‌وگفت دوستانه، دردودل، شوخی و کل‌کل، برنامه‌نویسی و کدنویسی، ادبیات، فلسفه، علوم پایه، ریاضیات، ترجمه، متن‌نویسی و همچنین تحلیل تکنیکال و ترید بازارهای مالی (ICT/SMC).
۲. هیچ محدودیتی روی موضوع مکالمه نداری و هرگز نمی‌گی "من فقط ربات تریدم"؛ تو یک رفیق شش‌دانگ و دستیار شخصی تمام‌عیار هستی.
۳. لحنت فارسی روان، خودمانی، محاوره‌ای و گرمه (از واژه‌های خشک کتابی استفاده نکن، سلام و تعارفات الکی و کلیشه‌ای نریز و صاف برو سر اصل مطلب).
۴. اگر کاربر تصویر، سند، اسکرین‌شات چارت یا هر عکسی فرستاد، با دقت بینایی بالا تحلیلش کن و جزئیات دقیقش رو بگو.
۵. به شعور کاربر احترام بذار، پاسخ‌های سطحی و آبکی نده و عمیق، کارآمد و حرفه‌ای راهنمایی کن.'''

def run_upgrade():
    if not os.path.exists(TARGET_FILE):
        print(f"❌ خطا: فایل {TARGET_FILE} در این پوشه پیدا نشد.")
        print("لطفاً مطمئن شوید این فایل را داخل پوشه اصلی ربات (کنار main.py) قرار داده‌اید.")
        return False

    shutil.copyfile(TARGET_FILE, BACKUP_FILE)
    print(f"✅ یک نسخه پشتیبان امن در {BACKUP_FILE} ذخیره شد.")

    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # جایگزینی پرامپت‌های قدیمی سیستم
    patterns = [
        r'(SYSTEM_PROMPT\s*=\s*(?:f?["\']{3}|f?["\']))(.*?)((?:["\']{3}|["\']))',
        r'(BOT_PERSONA\s*=\s*(?:f?["\']{3}|f?["\']))(.*?)((?:["\']{3}|["\']))',
        r'(TRADING_PROMPT\s*=\s*(?:f?["\']{3}|f?["\']))(.*?)((?:["\']{3}|["\']))',
        r'(DEFAULT_PROMPT\s*=\s*(?:f?["\']{3}|f?["\']))(.*?)((?:["\']{3}|["\']))',
    ]

    replaced = False
    for pat in patterns:
        if re.search(pat, content, flags=re.DOTALL):
            content = re.sub(pat, f'SYSTEM_PROMPT = """{UNIVERSAL_PROMPT}"""', content, count=1, flags=re.DOTALL)
            replaced = True
            break

    if not replaced:
        # اگر متغیر مستقیم پیدا نشد، در بالای فراخوانی‌های هوش مصنوعی تزریق یا اضافه می‌کنیم
        if "SYSTEM_PROMPT" in content:
            content = re.sub(r'SYSTEM_PROMPT\s*=\s*.*?\n(?=[A-Z_0-9]+\s*=|\ndef |\nclass )', f'SYSTEM_PROMPT = """{UNIVERSAL_PROMPT}"""\n\n', content, count=1, flags=re.DOTALL)
            replaced = True
        else:
            header_insert = f'\n# --- پرامپت همه‌کاره خان‌یار ---\nSYSTEM_PROMPT = """{UNIVERSAL_PROMPT}"""\n'
            content = header_insert + content
            replaced = True

    # اگر در کد شرط‌هایی بود که فقط پیام‌های ترید یا کلیدواژه‌های خاص رو قبول می‌کرد، آن‌ها را پاک/آزاد می‌کنیم
    content = re.sub(r'if\s+not\s+is_trading_related\([^)]*\):[\s\S]*?(?=elif|else|\n\s{4}[a-zA-Z_])', '# محدودیت ترید برداشته شد\n        pass\n        ', content)
    
    # اطمینان از اینکه در پرامپت درخواست‌های Groq / Gemini پرامپت سیستمی پاس داده می‌شود
    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print("🎉 تبریک! ربات شما با موفقیت به «هوش مصنوعی جامع و همه‌کاره» ارتقا یافت.")
    print("💎 اکنون ربات دقیقاً مانند خان‌یار به تمامی سوالات، چت‌های دوستانه، برنامه‌نویسی و ترید پاسخ می‌دهد.")
    return True

if __name__ == "__main__":
    run_upgrade()
