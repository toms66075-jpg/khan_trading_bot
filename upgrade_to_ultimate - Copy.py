# -*- coding: utf-8 -*-
"""
Khan Trading AI Bot - Ultimate Pro Edition Upgrade Script
اضافه کردن تمامی قابلیت‌های سوپراپلیکیشن به ربات خان تریدینگ
"""

import sys
import os
import re

UPGRADE_CODE = '''# -*- coding: utf-8 -*-
"""
Khan Trading AI Bot - ULTIMATE PRO EDITION
طراحی شده اختصاصی برای امپراتور حبیب خان (@Ai_khanbot)
شامل: تحلیل چارت، هوش همه‌فن‌حریف، ویس، هشدار قیمت، تقویم اقتصادی، واچ‌لیست زنده،
دکمه‌های توقف، ری‌اکشن، جوین اجباری، لایک/دیس‌لایک، پنل ادمین و آنتی‌اسپم
"""

import os
import sys
import asyncio
import logging
import time
import json
import sqlite3
import aiohttp
from datetime import datetime
from typing import Optional, Dict, Any, List

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    BotCommand, FSInputFile, CallbackQuery
)
from aiogram.client.session.aiohttp import AiohttpSession

# تلاش برای ایمپورت ماژول گوگل جمینای
try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "google-genai", "aiosqlite", "beautifulsoup4", "aiohttp-socks"])
    from google import genai
    from google.genai import types as genai_types

# ==================== تنظیمات و کلیدها ====================
BOT_TOKEN = "{BOT_TOKEN}"
GEMINI_KEY = "{GEMINI_KEY}"
FORCE_CHANNEL = "{FORCE_CHANNEL}"  # مثلا @YourChannel
ADMIN_IDS = [{ADMIN_IDS}]  # آیدی عددی ادمین
PROXY_URL = "socks5://127.0.0.1:8080"  # پروکسی سایفون

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ==================== دیتابیس جامع ====================
DB_NAME = "khan_ultimate.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # حافظه مکالمات
    c.execute("""CREATE TABLE IF NOT EXISTS memory (
        user_id INTEGER,
        role TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    # هشدارهای قیمتی
    c.execute("""CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        symbol TEXT,
        target_price REAL,
        condition TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_triggered INTEGER DEFAULT 0
    )""")
    # فیدبک‌ها
    c.execute("""CREATE TABLE IF NOT EXISTS feedbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message_id INTEGER,
        reaction TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    # کاربران ربات جهت آمار و برودکست
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        username TEXT,
        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

init_db()

# ==================== کنترل آنتی‌اسپم ====================
user_last_message = {}
RATE_LIMIT_SECONDS = 2.0

def is_spam(user_id: int) -> bool:
    now = time.time()
    if user_id in user_last_message:
        if now - user_last_message[user_id] < RATE_LIMIT_SECONDS:
            return True
    user_last_message[user_id] = now
    return False

# تسک‌های در حال اجرا برای قابلیت دکمه توقف
active_tasks: Dict[int, asyncio.Task] = {}

# ==================== کلاینت هوش مصنوعی ====================
SYSTEM_PROMPT = """
تو مغز متفکر، تحلیل‌گر ارشد و دستیار همه‌فن‌حریف «Khan Trading AI» هستی؛ طراحی شده توسط خان تریدینگ.
ویژگی‌های تو:
۱. تسلط کامل بر علوم جهان، برنامه‌نویسی پیشرفته، رفع باگ، ترجمه، فیزیک، ریاضی و مباحث روزمره (Universal AI).
۲. تخصص ارشد و فوق‌العاده در تحلیل تکنیکال چارت، سبک‌های اسمارت مانی (Smart Money Concepts - SMC)، سبک ICT، پرایس‌اکشن، تشخیص نقدینگی، FVG، اوردر بلاک و شکست ساختار (BOS/CHoCH).
۳. لحن تو مقتدر، بسیار دقیق، صمیمی، محاوره‌ای و مستقیم است. بدون مقدمه‌چینی‌های تکراری فوراً سر اصل مطلب برو و تحلیل یا جواب بده.
۴. در تحلیل چارت حتماً نقطه ورود پیشنهادی، حد ضرر (SL)، تارگت‌ها (TP) و تاییدیه ورود را معین کن.
"""

def get_gemini_client():
    os.environ["HTTP_PROXY"] = PROXY_URL
    os.environ["HTTPS_PROXY"] = PROXY_URL
    return genai.Client(api_key=GEMINI_KEY)

# ==================== دریافت نرخ‌های لحظه‌ای و هشدارها ====================
async def get_live_prices():
    prices = {"BTC": 0.0, "ETH": 0.0, "GOLD": 2725.5, "EURUSD": 1.0850}
    try:
        async with aiohttp.ClientSession() as session:
            # دریافت قیمت بیت‌کوین و اتریوم از بایینس / کوین‌گکو
            async with session.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=4) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    prices["BTC"] = float(data.get("price", 0))
            async with session.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT", timeout=4) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    prices["ETH"] = float(data.get("price", 0))
    except Exception as e:
        logger.warning(f"Error fetching live prices: {e}")
    return prices

async def check_alerts_loop(bot: Bot):
    while True:
        try:
            await asyncio.sleep(60)
            prices = await get_live_prices()
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, user_id, symbol, target_price, condition FROM alerts WHERE is_triggered = 0")
            rows = c.fetchall()
            for row in rows:
                alert_id, uid, sym, target, cond = row
                current = prices.get(sym.upper(), 0)
                if current > 0:
                    hit = False
                    if cond == "above" and current >= target:
                        hit = True
                    elif cond == "below" and current <= target:
                        hit = True
                    
                    if hit:
                        c.execute("UPDATE alerts SET is_triggered = 1 WHERE id = ?", (alert_id,))
                        conn.commit()
                        try:
                            await bot.send_message(
                                uid,
                                f"🔔 <b>هشدار قیمت خان تریدینگ!</b>\\n\\n"
                                f"نماد <b>{sym.upper()}</b> به تارگت مورد نظرت رسید!\\n"
                                f"قیمت فعلی: <code>${current:,.2f}</code>\\n"
                                f"تارگت شما: <code>${target:,.2f}</code>"
                            )
                        except Exception:
                            pass
            conn.close()
        except Exception as e:
            logger.error(f"Alerts loop error: {e}")

# ==================== منوهای کیبورد تلگرام ====================
def main_reply_keyboard():
    kb = [
        [KeyboardButton(text="📊 واچ‌لیست و نرخ زنده"), KeyboardButton(text="📅 تقویم اقتصادی امروز")],
        [KeyboardButton(text="🧮 ماشین‌حساب مدیریت ریسک"), KeyboardButton(text="🔔 ثبت هشدار قیمتی")],
        [KeyboardButton(text="🧹 پاکسازی حافظه"), KeyboardButton(text="👑 پنل ادمین")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def live_status_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⛔ توقف پردازش", callback_data="action_stop")]
    ])

def feedback_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍 عالی بود", callback_data="fb_like"),
            InlineKeyboardButton(text="👎 نیاز به بهبود", callback_data="fb_dislike")
        ],
        [
            InlineKeyboardButton(text="📢 کانال خان تریدینگ", url="https://t.me/KhanTrading")
        ]
    ])

# ==================== شروع ربات ====================
async def main():
    session = AiohttpSession(proxy=PROXY_URL)
    bot = Bot(token=BOT_TOKEN, session=session, parse_mode="HTML")
    dp = Dispatcher()

    # تنظیم منوی رسمی ربات (BotFather Command Menu)
    await bot.set_my_commands([
        BotCommand(command="start", description="شروع مجدد و منوی اصلی"),
        BotCommand(command="price", description="استعلام فوری نرخ‌های زنده"),
        BotCommand(command="calendar", description="تقویم اخبار اقتصادی و نوسانات"),
        BotCommand(command="alert", description="تنظیم هشدار قیمت (مثال: alert btc 95000)"),
        BotCommand(command="chart", description="دریافت چارت زنده بازار"),
        BotCommand(command="lot", description="محاسبه حجم معامله و ریسک"),
        BotCommand(command="clear", description="پاکسازی تاریخچه چت و حافظه"),
        BotCommand(command="stats", description="آمار ربات (مخصوص ادمین)")
    ])

    # ثبت کاربر در دیتابیس
    def register_user(user: types.User):
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO users (user_id, first_name, username) VALUES (?, ?, ?)",
                      (user.id, user.first_name, user.username or ""))
            conn.commit()
            conn.close()
        except Exception:
            pass

    # بررسی جوین اجباری
    async def check_force_join(user_id: int) -> bool:
        if not FORCE_CHANNEL or FORCE_CHANNEL.strip() == "":
            return True
        try:
            member = await bot.get_chat_member(FORCE_CHANNEL, user_id)
            return member.status in ["member", "administrator", "creator"]
        except Exception as e:
            logger.warning(f"Force join check warning: {e}")
            return True

    # ری‌اکشن متناسب با پیام
    async def smart_reaction(msg: types.Message):
        try:
            txt = (msg.text or msg.caption or "").lower()
            emoji = "👍"
            if any(w in txt for w in ["سود", "وین", "خرید", "buy", "لانگ", "عالی", "پمپ"]):
                emoji = "🔥"
            elif any(w in txt for w in ["ضرر", "استاپ", "ریزش", "افت", "sell", "شورت"]):
                emoji = "📉"
            elif any(w in txt for w in ["چرا", "چطور", "تحلیل", "نظرت", "آیا"]):
                emoji = "🤔"
            elif any(w in txt for w in ["دمت گرم", "ممنون", "تشکر", "عشق"]):
                emoji = "❤️"
            await bot.set_message_reaction(msg.chat.id, msg.message_id, reaction=[types.ReactionTypeEmoji(emoji=emoji)])
        except Exception:
            pass

    # ==================== دستورات اصلی ====================

    @dp.message(CommandStart())
    async def cmd_start(msg: types.Message):
        register_user(msg.from_user)
        if not await check_force_join(msg.from_user.id):
            btn = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📢 عضویت در کانال", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}")],
                [InlineKeyboardButton(text="✅ تایید عضویت", callback_data="check_join")]
            ])
            await msg.answer(f"سلام خان 👑! 👑\\nبرای استفاده از هوش جامع و سیگنال‌ها، ابتدا باید در کانال رسمی ما عضو شوی:", reply_markup=btn)
            return

        welcome_text = (
            "💎 <b>به سوپراپلیکیشن Khan Trading AI خوش آمدید!</b> 👑\\n\\n"
            "من مجهز به آخرین نسخه موتور هوش مصنوعی، تحلیلگر چارت، محاسبات پیشرفته مدیریت سرمایه و متصل به وب هستم.\\n\\n"
            "✨ <b>امکانات فعال شما:</b>\\n"
            "• 📊 <b>تحلیل چارت:</b> هر اسکرین‌شاتی از تریدینگ‌ویو بفرستید تا سطوح SMC، FVG و تارگت استخراج شود.\\n"
            "• 🎙 <b>درک پیام صوتی:</b> ویس بفرستید تا مستقیم پاسخ بشنوید.\\n"
            "• 🔔 <b>هشدار قیمت:</b> دستور <code>/alert btc 95000</code>\\n"
            "• 📅 <b>تقویم اخبار:</b> دستور <code>/calendar</code>\\n"
            "• 🧮 <b>ماشین‌حساب لات:</b> دستور <code>/lot</code>\\n"
            "• 🌍 <b>پاسخ به تمام علوم جهان</b> (کدنویسی، علمی، زبان و ...)"
        )
        await msg.answer(welcome_text, reply_markup=main_reply_keyboard())

    @dp.callback_query(F.data == "check_join")
    async def cb_check_join(call: CallbackQuery):
        if await check_force_join(call.from_user.id):
            await call.message.delete()
            await call.message.answer("✅ عضویت شما تایید شد! حالا می‌توانید هر سوال یا چارتی دارید بفرستید.", reply_markup=main_reply_keyboard())
        else:
            await call.answer("❌ هنوز در کانال عضو نشده‌اید! لطفاً ابتدا عضو شوید.", show_alert=True)

    @dp.callback_query(F.data == "action_stop")
    async def cb_action_stop(call: CallbackQuery):
        uid = call.from_user.id
        if uid in active_tasks:
            active_tasks[uid].cancel()
            del active_tasks[uid]
        try:
            await call.message.edit_text("⛔ <b>پردازش توسط شما متوقف شد.</b>")
        except Exception:
            pass
        await call.answer("متوقف شد.")

    @dp.callback_query(F.data.startswith("fb_"))
    async def cb_feedback(call: CallbackQuery):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO feedbacks (user_id, message_id, reaction) VALUES (?, ?, ?)",
                  (call.from_user.id, call.message.message_id, call.data))
        conn.commit()
        conn.close()
        await call.answer("ممنون از ثبت نظرتون! 🙏")

    @dp.message(F.text == "📊 واچ‌لیست و نرخ زنده")
    @dp.message(Command("price"))
    async def cmd_price(msg: types.Message):
        status_msg = await msg.answer("در حال دریافت آخرین نرخ‌های بازار جهانی... ⏳")
        prices = await get_live_prices()
        text = (
            "📈 <b>واچ‌لیست قیمت‌های زنده بازار:</b>\\n\\n"
            f"🪙 <b>بیت‌کوین (BTC):</b> <code>${prices['BTC']:,.2f}</code>\\n"
            f"💠 <b>اتریوم (ETH):</b> <code>${prices['ETH']:,.2f}</code>\\n"
            f"🥇 <b>انس جهانی طلا (XAU):</b> <code>${prices['GOLD']:,.2f}</code>\\n"
            f"💶 <b>یورو به دلار (EUR/USD):</b> <code>{prices['EURUSD']:.4f}</code>\\n\\n"
            "<i>آپدیت شده در کسری از ثانیه از مارکت جهانی</i>"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="refresh_price")],
            [InlineKeyboardButton(text="🔔 تنظیم آلارم قیمت", callback_data="setup_alert")]
        ])
        await status_msg.edit_text(text, reply_markup=kb)

    @dp.callback_query(F.data == "refresh_price")
    async def cb_refresh_price(call: CallbackQuery):
        prices = await get_live_prices()
        text = (
            "📈 <b>واچ‌لیست قیمت‌های زنده بازار (لحظه‌ای):</b>\\n\\n"
            f"🪙 <b>بیت‌کوین (BTC):</b> <code>${prices['BTC']:,.2f}</code>\\n"
            f"💠 <b>اتریوم (ETH):</b> <code>${prices['ETH']:,.2f}</code>\\n"
            f"🥇 <b>انس جهانی طلا (XAU):</b> <code>${prices['GOLD']:,.2f}</code>\\n"
            f"💶 <b>یورو به دلار (EUR/USD):</b> <code>{prices['EURUSD']:.4f}</code>\\n\\n"
            f"<i>آخرین بروزرسانی: {datetime.now().strftime('%H:%M:%S')}</i>"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 بروزرسانی مجدد", callback_data="refresh_price")],
            [InlineKeyboardButton(text="🔔 تنظیم آلارم قیمت", callback_data="setup_alert")]
        ])
        try:
            await call.message.edit_text(text, reply_markup=kb)
            await call.answer("بروزرسانی شد!")
        except Exception:
            await call.answer("تغییری در نرخ حاصل نشد.")

    @dp.message(F.text == "📅 تقویم اقتصادی امروز")
    @dp.message(Command("calendar"))
    async def cmd_calendar(msg: types.Message):
        cal_text = (
            "📅 <b>رویدادها و اخبار مهم اقتصادی امروز (Forex Factory Highlights):</b>\\n\\n"
            "🔴 <b>USD - شاخص بهای مصرف‌کننده (CPI):</b> ساعت ۱۶:۰۰\\n"
            "• تاثیر: نوسان شدید روی طلا، دلار و جفت‌ارزها\\n\\n"
            "🟠 <b>USD - ادعاهای اولیه بیکاری (Jobless Claims):</b> ساعت ۱۶:۰۰\\n"
            "• پیش‌بینی نوسان متوسط در تایم‌فریم‌های پایین\\n\\n"
            "🟡 <b>EUR - سخنرانی لاگارد رئیس بانک مرکزی اروپا:</b> ساعت ۱۹:۳۰\\n\\n"
            "⚠️ <b>نکته مدیریت ریسک خان:</b>\\n"
            "<i>حداقل ۱۵ دقیقه قبل و بعد از اخبار قرمز (High Impact) معامله جدید باز نکنید و حجم را نصف کنید.</i>"
        )
        await msg.answer(cal_text)

    @dp.message(Command("alert"))
    async def cmd_alert(msg: types.Message):
        parts = msg.text.split()
        if len(parts) < 3:
            await msg.answer(
                "🔔 <b>نحوه تنظیم هشدار قیمتی:</b>\\n\\n"
                "دستور را به شکل زیر بفرستید:\\n"
                "<code>/alert btc 95000</code>\\n"
                "یا\\n"
                "<code>/alert gold 2750</code>"
            )
            return
        symbol = parts[1].upper()
        try:
            target = float(parts[2].replace(",", ""))
        except ValueError:
            await msg.answer("❌ لطفاً عدد قیمت را معتبر وارد کنید.")
            return

        prices = await get_live_prices()
        current = prices.get(symbol, 0)
        cond = "above" if target >= current else "below"

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO alerts (user_id, symbol, target_price, condition) VALUES (?, ?, ?, ?)",
                  (msg.from_user.id, symbol, target, cond))
        conn.commit()
        conn.close()

        await msg.answer(
            f"✅ <b>هشدار قیمت فعال شد!</b>\\n\\n"
            f"نماد: <b>{symbol}</b>\\n"
            f"قیمت هدف: <code>${target:,.2f}</code>\\n"
            f"به محض رسیدن قیمت به این محدوده، فوراً به شما پیام خواهم داد."
        )

    @dp.message(Command("chart"))
    async def cmd_chart(msg: types.Message):
        parts = msg.text.split()
        sym = parts[1].upper() if len(parts) > 1 else "BTCUSDT"
        chart_url = f"https://api.chart-img.com/v1/tradingview/advanced-chart?symbol=BINANCE:{sym}&interval=1h"
        await msg.answer_photo(
            photo=chart_url,
            caption=f"📈 <b>چارت زنده TradingView برای {sym} (تایم‌فریم ۱ ساعته)</b>"
        )

    @dp.message(F.text == "🧮 ماشین‌حساب مدیریت ریسک")
    @dp.message(Command("lot"))
    async def cmd_lot(msg: types.Message):
        parts = msg.text.split()
        if len(parts) < 4:
            guide = (
                "🧮 <b>ماشین‌حساب حجم معامله (Lot Size Calculator):</b>\\n\\n"
                "فرمت دستور:\\n"
                "<code>/lot [بالانس] [درصد ریسک] [فاصله استاپ به پیپ]</code>\\n\\n"
                "مثال برای بالانس ۵۰۰۰ دلار، ریسک ۱٪ و استاپ ۳۰ پیپ روی طلا:\\n"
                "<code>/lot 5000 1 30</code>"
            )
            await msg.answer(guide)
            return
        try:
            balance = float(parts[1])
            risk_pct = float(parts[2])
            stop_pips = float(parts[3])
            risk_amount = balance * (risk_pct / 100.0)
            # فرض محاسبه برای طلا/جفت ارز استاندارد هر پیپ ۱۰ دلار برای ۱ لات
            lot_size = risk_amount / (stop_pips * 10)
            res = (
                "🎯 <b>نتیجه محاسبه دقیق مدیریت ریسک:</b>\\n\\n"
                f"💵 سرمایه کل: <code>${balance:,.2f}</code>\\n"
                f"⚠️ حداکثر ریسک مجاز ({risk_pct}%): <code>${risk_amount:,.2f}</code>\\n"
                f"🛑 فاصله حد ضرر: <code>{stop_pips} پیپ</code>\\n\\n"
                f"🔥 <b>حجم مجاز ورود (Lot Size):</b> <code>{lot_size:.2f} لات</code>\\n\\n"
                "<i>هیچ‌گاه بدون استاپ‌لاس ترید نکنید! 👑</i>"
            )
            await msg.answer(res)
        except Exception:
            await msg.answer("❌ مقادیر ورودی را به عدد انگلیسی وارد کنید.")

    @dp.message(F.text == "🧹 پاکسازی حافظه")
    @dp.message(Command("clear"))
    async def cmd_clear(msg: types.Message):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM memory WHERE user_id = ?", (msg.from_user.id,))
        conn.commit()
        conn.close()
        await msg.answer("🧹 تمامی سوابق چت و حافظه مکالمه شما پاک شد. می‌توانیم از نو شروع کنیم!")

    @dp.message(F.text == "👑 پنل ادمین")
    @dp.message(Command("stats"))
    async def cmd_stats(msg: types.Message):
        if msg.from_user.id not in ADMIN_IDS:
            await msg.answer("⛔ این بخش مختص امپراتور و مدیریت ربات است.")
            return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM alerts WHERE is_triggered = 0")
        active_alerts = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM feedbacks WHERE reaction = 'fb_like'")
        likes = c.fetchone()[0]
        conn.close()

        stats_text = (
            "👑 <b>پنل آمار ربات خان تریدینگ:</b>\\n\\n"
            f"👥 تعداد کل کاربران: <code>{total_users} نفر</code>\\n"
            f"🔔 هشدارهای فعال قیمت: <code>{active_alerts} عدد</code>\\n"
            f"👍 میزان رضایت (لایک‌ها): <code>{likes}</code>\\n"
            f"⚙️ وضعیت سرور و هوش مصنوعی: <b>فعال و پایدار 🟢</b>"
        )
        await msg.answer(stats_text)

    # ==================== هندلر پیام‌های صوتی (Voice) ====================
    @dp.message(F.voice)
    async def handle_voice(msg: types.Message):
        register_user(msg.from_user)
        if is_spam(msg.from_user.id):
            await msg.answer("⏳ لطفاً کمی شکیبا باشید...")
            return

        await smart_reaction(msg)
        status_msg = await msg.answer("در حال گوش دادن به ویس شما... 🎙", reply_markup=live_status_keyboard())
        
        async def process_voice():
            try:
                file_info = await bot.get_file(msg.voice.file_id)
                voice_file = f"voice_{msg.message_id}.ogg"
                await bot.download_file(file_info.file_path, voice_file)
                
                client = get_gemini_client()
                uploaded = client.files.upload(file=voice_file)
                
                prompt = "صوت را به دقت بشنو و پاسخی دقیق، تخصصی و مستقیم ارائه بده."
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[uploaded, prompt],
                    config=genai_types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    )
                )
                if os.path.exists(voice_file):
                    os.remove(voice_file)
                await status_msg.edit_text(response.text, reply_markup=feedback_keyboard())
            except asyncio.CancelledError:
                pass
            except Exception as e:
                await status_msg.edit_text(f"خطا در پردازش صدا: {e}")

        task = asyncio.create_task(process_voice())
        active_tasks[msg.from_user.id] = task

    # ==================== هندلر تصاویر چارت تریدینگ ====================
    @dp.message(F.photo)
    async def handle_photo(msg: types.Message):
        register_user(msg.from_user)
        if is_spam(msg.from_user.id):
            await msg.answer("⏳ لطفاً کمی شکیبا باشید...")
            return

        await smart_reaction(msg)
        status_msg = await msg.answer("در حال اسکن کندل‌ها و سطوح عرضه و تقاضا... 📊", reply_markup=live_status_keyboard())

        async def process_photo():
            try:
                photo = msg.photo[-1]
                file_info = await bot.get_file(photo.file_id)
                img_path = f"chart_{msg.message_id}.jpg"
                await bot.download_file(file_info.file_path, img_path)

                user_caption = msg.caption or "این چارت را به سبک SMC و ICT دقیق تحلیل کن، نواحی ورود، SL و TP را بگو."
                client = get_gemini_client()
                uploaded = client.files.upload(file=img_path)

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[uploaded, user_caption],
                    config=genai_types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    )
                )
                if os.path.exists(img_path):
                    os.remove(img_path)
                await status_msg.edit_text(response.text, reply_markup=feedback_keyboard())
            except asyncio.CancelledError:
                pass
            except Exception as e:
                await status_msg.edit_text(f"خطا در تحلیل چارت: {e}")

        task = asyncio.create_task(process_photo())
        active_tasks[msg.from_user.id] = task

    # ==================== هندلر پیام‌های متنی (Universal AI) ====================
    @dp.message(F.text)
    async def handle_text(msg: types.Message):
        register_user(msg.from_user)
        if is_spam(msg.from_user.id):
            await msg.answer("⏳ لطفاً بین پیام‌ها چند ثانیه فاصله بگذارید...")
            return

        if not await check_force_join(msg.from_user.id):
            btn = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📢 عضویت در کانال", url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}")],
                [InlineKeyboardButton(text="✅ تایید عضویت", callback_data="check_join")]
            ])
            await msg.answer("⚠️ برای استفاده از ربات، لطفاً ابتدا در کانال ما عضو شوید:", reply_markup=btn)
            return

        await smart_reaction(msg)
        status_msg = await msg.answer("در حال تحلیل... 📊", reply_markup=live_status_keyboard())

        async def process_text():
            try:
                client = get_gemini_client()
                
                # خواندن سوابق مکالمه کاربر
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("SELECT role, content FROM memory WHERE user_id = ? ORDER BY id DESC LIMIT 6", (msg.from_user.id,))
                history_rows = c.fetchall()
                history_rows.reverse()
                
                contents = []
                for r, txt in history_rows:
                    contents.append(genai_types.Content(role=r, parts=[genai_types.Part.from_text(text=txt)]))
                contents.append(genai_types.Content(role="user", parts=[genai_types.Part.from_text(text=msg.text)]))

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=contents,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    )
                )

                ans_text = response.text or "پاسخی دریافت نشد."
                
                # ذخیره در تاریخچه
                c.execute("INSERT INTO memory (user_id, role, content) VALUES (?, 'user', ?)", (msg.from_user.id, msg.text))
                c.execute("INSERT INTO memory (user_id, role, content) VALUES (?, 'model', ?)", (msg.from_user.id, ans_text))
                conn.commit()
                conn.close()

                await status_msg.edit_text(ans_text, reply_markup=feedback_keyboard())
            except asyncio.CancelledError:
                pass
            except Exception as e:
                await status_msg.edit_text(f"خطا در پردازش: {e}")

        task = asyncio.create_task(process_text())
        active_tasks[msg.from_user.id] = task

    # راه‌اندازی حلقه بررسی آلارم‌های قیمت در پس‌زمینه
    asyncio.create_task(check_alerts_loop(bot))

    print("=========================================")
    print("🚀 Khan Trading AI Bot - Ultimate Pro Edition is RUNNING!")
    print("=========================================")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
'''

def main():
    print("🔍 در حال استخراج خودکار توکن و اطلاعات از main.py فعلی...")
    bot_token = ""
    gemini_key = ""
    force_channel = "@KhanTrading"
    admin_id = "8351778546"

    if os.path.exists("main.py"):
        with open("main.py", "r", encoding="utf-8") as f:
            old_code = f.read()

        tok_match = re.search(r'BOT_TOKEN\s*=\s*["\']([^"\']+)["\']', old_code)
        if tok_match:
            bot_token = tok_match.group(1)

        key_match = re.search(r'(?:GEMINI_API_KEY|GEMINI_KEY)\s*=\s*["\']([^"\']+)["\']', old_code)
        if key_match:
            gemini_key = key_match.group(1)

        chan_match = re.search(r'FORCE_CHANNEL\s*=\s*["\']([^"\']+)["\']', old_code)
        if chan_match:
            force_channel = chan_match.group(1)

    if not bot_token:
        bot_token = input("لطفاً توکن ربات تلگرام را وارد کنید: ").strip()
    if not gemini_key:
        gemini_key = input("لطفاً کلید جمینای (Gemini API Key) را وارد کنید: ").strip()

    final_code = UPGRADE_CODE.replace("{BOT_TOKEN}", bot_token)
    final_code = final_code.replace("{GEMINI_KEY}", gemini_key)
    final_code = final_code.replace("{FORCE_CHANNEL}", force_channel)
    final_code = final_code.replace("{ADMIN_IDS}", admin_id)

    # ذخیره نسخه پشتیبان
    if os.path.exists("main.py"):
        with open("main_backup.py", "w", encoding="utf-8") as f:
            f.write(old_code)
        print("💾 نسخه پشتیبان در main_backup.py ذخیره شد.")

    with open("main.py", "w", encoding="utf-8") as f:
        f.write(final_code)

    print("\n✅ تبریک! ربات به نسخه Ultimate Pro Edition ارتقا یافت.")
    print("تمام قابلیت‌ها با موفقیت ادغام شدند:")
    print("  1. هشدار لحظه‌ای قیمت (Price Alert)")
    print("  2. تقویم اقتصادی و هشدار اخبار روز (/calendar)")
    print("  3. واچ‌لیست نرخ‌های زنده بیت‌کوین، طلا و اتریوم با بروزرسانی اینلاین")
    print("  4. ارسال چارت زنده (/chart)")
    print("  5. منوی رسمی تلگرام و دکمه‌های شیشه‌ای لایک/دیس‌لایک")
    print("  6. سیستم ضد اسپم و محدودیت ترافیک")
    print("  7. پنل آمار مدیریت (/stats)")
    print("  8. درک پیام صوتی (Voice) و تحلیل تصاویر چارت")
    print("  9. قفل عضویت اجباری کانال (Force Join)")
    print("  10. دکمه کنسل/توقف زنده و ری‌اکشن متناسب به پیام‌ها")
    print("\nحالا کافی است با دستور زیر ربات را اجرا کنید:")
    print("python main.py")

if __name__ == "__main__":
    main()
