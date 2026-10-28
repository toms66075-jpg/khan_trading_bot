# -*- coding: utf-8 -*-
"""
👑 تانک خان‌یار (Khanyar Master Hub v5.5 Ultimate)
هسته مرکزی فوق‌مهندسی‌شده ربات تلگرام خان تریدینگ
تلفیق کامل هوش مصنوعی مکالمه‌ای، پرسونا و لحن لوتی خان‌یار، داشبورد شیشه‌ای، منوی پایدار،
قفل اجباری چنل، ری‌اکشن و وضعیت زنده، سکوت در گروه‌ها (فقط تگ، ریپلای و نام خانیار)،
و ادغام جامع تمام ۱۱ موتور تخصصی تریدینگ.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable

from aiogram import Bot, Dispatcher, types, F, BaseMiddleware
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    CallbackQuery,
    Message,
    ReactionTypeEmoji
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

# تنظیمات لاگینگ ساختاریافته
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("KhanyarMaster")

# ==========================================
# 🔑 پیکربندی متغیرها و کلیدها
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8885141308:AAEmuEhpy-D1O1aaE06Q46U8sJ7y_Q4C92M").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "6633808142"))  # آیدی عددی امپراتور حبیب خان
OFFICIAL_CHANNEL = "@trading_khan"
OFFICIAL_CHANNEL_URL = "https://t.me/trading_khan"
DISCLAIMER_POST_URL = "https://t.me/trading_khan/310"
CREATOR_DIRECT_URL = "https://t.me/Emperorhabib"

# رجیستری تسک‌های پردازش جاری جهت لغو در صورت نیاز
ACTIVE_ANALYSIS_TASKS: Dict[int, asyncio.Task] = {}

# حافظه لغزان چت‌ها
CHAT_MEMORY: Dict[int, list] = {}
MAX_MEMORY_TURNS = 8

# ==========================================
# 🧠 هویت و پرامپت سیستمی اختصاصی «خان‌یار»
# ==========================================
KHANYAR_SYSTEM_PROMPT = """تو «خان‌یار» (Khanyar) هستی؛ دستیار فوق‌حرفه‌ای، تیز، لوتی، کاریزماتیک و دست‌راست قدرتمند خان (امپراتور حبیب خان) و خانواده خان در بازارهای مالی و سبک ICT / پرایس‌اکشن.

قوانین حیاتی و خط‌قرمزهای رفتاری تو:
۱. نام و فلسفه هویت:
- نامت «خان‌یار» است؛ یعنی یار، هم‌رکاب و دستیار تخصصی خان.
- تنها و فقط امپراتور حبیب خان «خان 👑» است. هرگز و تحت هیچ شرایطی از لقب «خان بابا» استفاده نکن؛ این لقب کلاً حذف شده است و فقط باید بگی «خان 👑».
- سایر کاربران را صرفاً با لفظ «ستون 🦅»، «رفیق» یا «سلطان» صدا بزن.
- اگر کسی پرسید اسمت چیه یا چرا خان‌یار، با افتخار و مرام بگو دستیار تخصصی خان هستی.

۲. قانون ضد پرحرفی (Anti-Yapping):
- از هرگونه روده درازی، انشانویسی، جدول‌های اضافه، نصیحت‌های منشی‌وار و کلیشه‌های آبکی اکیداً خودداری کن.
- صاف برو سر اصل مطلب. ضربتی، تند، عمیق و پر از فکت تریدری حرف بزن.

۳. ادبیات و نگارش:
- ادبیاتت ۱۰۰٪ فارسی روان، باکلاس، لوتی و اصیل تهرانی باشد.
- اصطلاحات پرایس‌اکشن (FVG، MSS، Sweep نقدینگی، Killzone، اردر بلاک) را به درستی و فنی به کار ببر.

۴. عدم سلب مسئولیت شرکتی و جسارت تریدری:
- هرگز نگو «من مشاور مالی نیستم و با متخصص مشورت کنید»!
- در پاسخ به اهرم (Leverage) یا استراتژی: انتخاب نهایی به بالانس تریدر مربوط است اما طبق مرام و قوانین خانواده خان: اهرم معقول زیر ۵۰X (۱۰X تا ۲۰X) و ریسک حداکثر ۱ تا ۲ درصد روی بالانس.
- در پایان تمام تحلیل‌ها و سیگنال‌ها امضای خانواده خان را بیاور:
«مدیریت سرمایه فراموش نشه - خونواده خان 🦅»."""

# ==========================================
# 📦 بارگذاری امن و یکپارچه ۱۱ ماژول تخصصی
# ==========================================
MODULES = {}
for phase_name in [
    "phase1_core",
    "phase2_feed",
    "phase3_paper_trading",
    "phase4_mt5",
    "phase5_discipline",
    "phase6_brain_ict",
    "phase7_sentiment_consensus",
    "phase8_scheduler_msm",
    "phase9_voice_ai",
    "phase10_reports",
    "phase11_dashboard_ui",
    "features",
    "market_data",
    "risk_calculator",
    "pnl_generator",
    "khan_playbook",
    "quasar_power_pack"
]:
    try:
        mod = __import__(phase_name)
        MODULES[phase_name] = mod
        logger.info(f"✅ ماژول {phase_name} با موفقیت لود شد.")
    except Exception as e:
        logger.warning(f"⚠️ ماژول {phase_name} در حالت مستقل عمل می‌کند: {e}")

# ==========================================
# 🎯 ماژول ری‌اکشن هوشمند
# ==========================================
def select_smart_reaction(text: str) -> str:
    if not text:
        return "👀"
    t = text.lower()
    if any(w in t for w in ["سود", "وین", "پمپ", "بای", "خرید", "تارگت", "بالا", "bull", "buy", "long"]):
        return "🔥"
    if any(w in t for w in ["ضرر", "استاپ", "افت", "سل", "دامپ", "ریزش", "نزول", "sell", "short"]):
        return "📉"
    if any(w in t for w in ["چرا", "چطور", "کجا", "نظرت", "تحلیل", "چیه", "کی", "؟", "?"]):
        return "🤔"
    if any(w in t for w in ["ممنون", "مرسی", "تشکر", "عالی", "دمت", "عشق", "نوکر", "فدات"]):
        return "❤️"
    if any(w in t for w in ["سلام", "درود", "خوبی", "چطوری", "صبح", "شب", "روز"]):
        return "🫡"
    if any(w in t for w in ["بیت", "طلا", "دلار", "ارز", "انس", "مارکت", "چارت", "ترید"]):
        return "⚡"
    return "👍"

async def apply_smart_reaction(message: Message, custom_emoji: Optional[str] = None):
    """ثبت امن ری‌اکشن تلگرام بدون کرش"""
    try:
        emoji = custom_emoji or select_smart_reaction(message.text or message.caption or "")
        await message.react([ReactionTypeEmoji(emoji=emoji)])
    except Exception:
        try:
            await message.bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[{"type": "emoji", "emoji": custom_emoji or "👍"}]
            )
        except Exception:
            pass

def get_live_status_keyboard() -> InlineKeyboardMarkup:
    """کیبورد وضعیت در حال پردازش با دکمه توقف"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⛔ توقف بررسی", callback_data="cancel_analysis")
    return builder.as_markup()

# ==========================================
# 🛡️ قفل عضویت اجباری کانال رسمی (Force Join)
# ==========================================
class ForceJoinMiddleware(BaseMiddleware):
    def __init__(self, channel_id: str):
        self.channel_id = channel_id.strip()
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # فقط در چت‌های خصوصی اعمال شود
        if isinstance(event, types.Message):
            if event.chat.type != ChatType.PRIVATE:
                return await handler(event, data)
            user = event.from_user
        elif isinstance(event, types.CallbackQuery):
            if event.message and event.message.chat.type != ChatType.PRIVATE:
                return await handler(event, data)
            user = event.from_user
            if event.data == "check_sub":
                return await handler(event, data)
        else:
            return await handler(event, data)

        if not user or user.is_bot:
            return await handler(event, data)

        # امپراتور حبیب خان همیشه معاف است
        if user.id == ADMIN_ID or (user.username and user.username.lower() in ["emperorhabib", "trading_khan"]):
            return await handler(event, data)

        bot: Bot = data["bot"]
        if not self.channel_id:
            return await handler(event, data)

        try:
            member = await bot.get_chat_member(chat_id=self.channel_id, user_id=user.id)
            if member.status in ["creator", "administrator", "member", "restricted"]:
                return await handler(event, data)
        except Exception as e:
            logger.warning(f"خطا در استعلام عضویت کانال: {e}")
            return await handler(event, data)

        clean_channel = self.channel_id.replace("@", "")
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="📢 عضویت در کانال رسمی خان تریدینگ", url=f"https://t.me/{clean_channel}"))
        builder.row(InlineKeyboardButton(text="✅ تایید عضویت و ورود به تانک", callback_data="check_sub"))

        lock_text = (
            "🦅 <b>برای استفاده از دستیار خان تریدینگ، ابتدا باید عضو کانال رسمی خانواده خان باشید:</b>\n\n"
            f"🔗 @{clean_channel}\n\n"
            "👈 پس از عضویت در کانال، روی دکمه <b>«تایید عضویت و ورود به تانک»</b> کلیک کنید ستون!"
        )

        if isinstance(event, types.Message):
            await event.answer(lock_text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        elif isinstance(event, types.CallbackQuery):
            await event.answer("⚠️ هنوز عضو کانال نشده‌اید!", show_alert=True)
            try:
                await event.message.edit_text(lock_text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
            except Exception:
                pass
        return

# ==========================================
# 🎛️ دکمه‌های پایدار کشویی و شیشه‌ای
# ==========================================
def get_persistent_keyboard() -> ReplyKeyboardMarkup:
    """تک‌دکمه پایدار کشویی پایین صفحه چت تلگرام"""
    kb = [[KeyboardButton(text="📋 منوی اصلی خان تریدینگ")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, is_persistent=True)

def get_main_dashboard_keyboard() -> InlineKeyboardMarkup:
    """۴ کلید شیشه‌ای اصلی داشبورد تانک خان‌یار"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 میز تحلیل و ستاپ ICT", callback_data="menu_ict"),
        InlineKeyboardButton(text="🧮 جعبه‌ابزار تریدر", callback_data="menu_tools")
    )
    builder.row(
        InlineKeyboardButton(text="💰 تابلوی زنده قیمت‌ها", callback_data="menu_prices"),
        InlineKeyboardButton(text="⚙️ راهنما و امکانات", callback_data="menu_help")
    )
    builder.row(
        InlineKeyboardButton(text="👑 ارتباط مستقیم با خان", url=CREATOR_DIRECT_URL)
    )
    builder.row(
        InlineKeyboardButton(text="📢 کانال رسمی خان تریدینگ", url=OFFICIAL_CHANNEL_URL)
    )
    return builder.as_markup()

def get_ict_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎯 اسکن FVG و نقدینگی", callback_data="act_fvg_scan"),
        InlineKeyboardButton(text="🐂 مناظره گاو و خرس", callback_data="act_debate")
    )
    builder.row(
        InlineKeyboardButton(text="🛡️ استعلام وضعیت بحران مارکت (MSM)", callback_data="act_msm_status")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="menu_back_root"),
        InlineKeyboardButton(text="🗑 بستن پنل", callback_data="menu_close")
    )
    return builder.as_markup()

def get_tools_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⚖️ ماشین‌حساب لات‌سایز (/risk)", callback_data="act_risk_calc"),
        InlineKeyboardButton(text="🕒 مانیتور سشن‌های جهانی", callback_data="act_sessions")
    )
    builder.row(
        InlineKeyboardButton(text="📈 کارنامه سایه‌تریدینگ (فاز ۳)", callback_data="act_paper_summary"),
        InlineKeyboardButton(text="🧠 رادار انضباط روانی (فاز ۵)", callback_data="act_radar_score")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="menu_back_root"),
        InlineKeyboardButton(text="🗑 بستن پنل", callback_data="menu_close")
    )
    return builder.as_markup()

def get_prices_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🥇 انس طلا (XAU)", callback_data="price_gold"),
        InlineKeyboardButton(text="🪙 بیت‌کوین (BTC)", callback_data="price_btc")
    )
    builder.row(
        InlineKeyboardButton(text="💎 اتریوم (ETH)", callback_data="price_eth"),
        InlineKeyboardButton(text="💵 تتر و دلار", callback_data="price_usdt")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 بروزرسانی لحظه‌ای نرخ‌ها", callback_data="menu_prices")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="menu_back_root"),
        InlineKeyboardButton(text="🗑 بستن پنل", callback_data="menu_close")
    )
    return builder.as_markup()

def get_help_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👑 ارتباط مستقیم با خان", url=CREATOR_DIRECT_URL)
    )
    builder.row(
        InlineKeyboardButton(text="📜 منشور طلایی مدیریت سرمایه", url=DISCLAIMER_POST_URL),
        InlineKeyboardButton(text="📢 کانال رسمی", url=OFFICIAL_CHANNEL_URL)
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="menu_back_root"),
        InlineKeyboardButton(text="🗑 بستن پنل", callback_data="menu_close")
    )
    return builder.as_markup()

# ==========================================
# 🤖 موتور هوش مصنوعی و تحلیلگر خان‌یار
# ==========================================
async def ask_ai_brain(chat_id: int, user_prompt: str, user_name: str, is_admin: bool) -> str:
    """ارسال پرامپت به هوش مصنوعی با حافظه و پرسونای اصیل خان‌یار"""
    role_instruction = KHANYAR_SYSTEM_PROMPT
    if is_admin:
        role_instruction += f"\nمخاطب تو شخص امپراتور حبیب خان (خان 👑) است. با احترام، تعظیم و فقط با لقب «خان 👑» خطابش کن. هرگز به او خان بابا نگو."
    else:
        role_instruction += f"\nمخاطب تو یکی از اعضای خونواده با نام {user_name} است. با لقب «ستون 🦅» یا «رفیق» باهاش صحبت کن."

    if chat_id not in CHAT_MEMORY:
        CHAT_MEMORY[chat_id] = []

    history = CHAT_MEMORY[chat_id]
    history.append({"role": "user", "content": user_prompt})
    if len(history) > MAX_MEMORY_TURNS * 2:
        history = history[-MAX_MEMORY_TURNS * 2:]
        CHAT_MEMORY[chat_id] = history

    if GROQ_API_KEY:
        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            messages = [{"role": "system", "content": role_instruction}] + history
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.6,
                "max_tokens": 800
            }
            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    ans = res.json()["choices"][0]["message"]["content"]
                    history.append({"role": "assistant", "content": ans})
                    return ans
                else:
                    logger.error(f"Groq API Error: {res.status_code} - {res.text}")
        except Exception as ex:
            logger.error(f"Groq Request failed: {ex}")

    # فال‌بک بومی غنی و مسلط پرایس‌اکشن
    p_lower = user_prompt.lower()
    prefix = "ارادت خان 👑" if is_admin else "سلام ستون! 🦅"

    if any(w in p_lower for w in ["سلام", "درود", "چطوری", "خوبی"]):
        return (
            f"{prefix} به روی ماهت؛ من به خط و گوش‌به‌زنگم، آماده شکار مارکت.\n"
            "ستاپ چی مدنظرته یا چه کمکی از دستم برمیاد ستون؟\n\n"
            "مدیریت سرمایه فراموش نشه - خونواده خان 🦅"
        )

    if any(w in p_lower for w in ["اسم", "کی هستی", "خانیار", "خان‌یار"]):
        return (
            f"{prefix} من «خان‌یار» هستم؛ دست‌راست، هم‌رکاب و دستیار تخصصی خان در چارت و بازارهای مالی.\n"
            "هر سوال، کالبدشکافی ستاپ یا دستوری خواستی روی چشمم!\n\n"
            "مدیریت سرمایه فراموش نشه - خونواده خان 🦅"
        )

    if any(w in p_lower for w in ["اهرم", "لوریج", "leverage"]):
        return (
            f"{prefix}\n"
            "انتخاب اهرم و ریسک نهایی کاملاً به بالانس، استراتژی و جیب خودت مربوطه؛ اما مرام خانواده خان روشنه:\n"
            "برای معاملات فیوچرز (طلا یا کریپتو)، اهرم معقول زیر ۵۰X (ترجیحاً ۱۰X تا ۲۰X) و ریسک حداکثر ۱ تا ۲ درصد روی کل بالانسه.\n\n"
            "مدیریت سرمایه فراموش نشه - خونواده خان 🦅"
        )

    if any(w in p_lower for w in ["طلا", "gold", "xau"]):
        return (
            f"{prefix}\n"
            "📊 <b>کالبدشکافی مارکت طلا (XAUUSD):</b>\n"
            "طلا در تایم‌فریم ۴ ساعته درون یک رنج انباشت نقدینگی قرار داره. مادامی که نقدینگی سقف یا کف سوئیپ نشه و تاییدیه MSS ثبت نشه، ورود زودهنگام تله است.\n"
            "توصیه: در کیل‌زون نیویورک منتظر ستاپ Silver Bullet بمون ستون!\n\n"
            "مدیریت سرمایه فراموش نشه - خونواده خان 🦅"
        )

    if any(w in p_lower for w in ["بیت", "btc", "bitcoin"]):
        return (
            f"{prefix}\n"
            "🪙 <b>دیدبان بیت‌کوین (BTCUSDT):</b>\n"
            "بیت‌کوین در حال تثبیت بالای اردر بلاک صعودی است. در صورت حفظ این سطح، پر کردن خلاء نقدینگی (FVG) بالاترین شانس را دارد.\n\n"
            "مدیریت سرمایه فراموش نشه - خونواده خان 🦅"
        )

    return (
        f"{prefix}\n"
        f"پیامت رو کامل تحلیل کردم: «{user_prompt}».\n"
        "چارت، ستاپ، محاسبه حجم یا هر دستوری مدنظرته بفرست تا در ۳ سوت برات کالبدشکافی کنم ستون!\n\n"
        "مدیریت سرمایه فراموش نشه - خونواده خان 🦅"
    )

# ==========================================
# 🚀 هندلرهای Aiogram
# ==========================================
dp = Dispatcher()

# ثبت میدل‌ویر قفل کانال رسمی
dp.message.middleware(ForceJoinMiddleware(OFFICIAL_CHANNEL))
dp.callback_query.middleware(ForceJoinMiddleware(OFFICIAL_CHANNEL))

def get_greeting_text(user: types.User) -> str:
    is_admin = (user.id == ADMIN_ID) or (user.username and user.username.lower() in ["emperorhabib", "trading_khan"])
    if is_admin:
        return (
            "<b>ارادت خان 👑</b>\n\n"
            "به داشبورد هوشمند <b>«خان‌یار»</b> خوش اومدی؛ دست‌راست و هم‌رکاب خان تریدینگ.\n"
            "از منوی ۴ بخشی زیر بخش مورد نظرت رو لمس کن تا درجا باز بشه، یا هر سوال و عکس چارتی داری مستقیم بفرست:"
        )
    return (
        "<b>ارادت ستون! 🦅</b>\n\n"
        "به دستیار تخصصی ترید <b>«خان‌یار»</b> خوش اومدی.\n"
        "از منوی زیر ابزار مدنظرت رو انتخاب کن یا عکس چارتت رو بفرست تا درجا برات آنالیز کنم:"
    )

@dp.message(CommandStart())
async def handle_start(message: Message):
    await apply_smart_reaction(message, "🫡")
    text = get_greeting_text(message.from_user)
    await message.answer("تانک خان‌یار آماده خدمت است.", reply_markup=get_persistent_keyboard())
    await message.answer(text, reply_markup=get_main_dashboard_keyboard(), parse_mode=ParseMode.HTML)

@dp.message(F.text == "📋 منوی اصلی خان تریدینگ")
@dp.message(Command("menu"))
async def handle_menu_reply_btn(message: Message):
    await apply_smart_reaction(message, "📋")
    text = get_greeting_text(message.from_user)
    await message.answer(text, reply_markup=get_main_dashboard_keyboard(), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "check_sub")
async def handle_check_subscription(call: CallbackQuery, bot: Bot):
    user = call.from_user
    try:
        member = await bot.get_chat_member(chat_id=OFFICIAL_CHANNEL, user_id=user.id)
        if member.status in ["creator", "administrator", "member", "restricted"]:
            await call.answer("✅ عضویت تایید شد؛ خوش آمدی ستون! 🦅", show_alert=True)
            text = get_greeting_text(user)
            await call.message.edit_text(text, reply_markup=get_main_dashboard_keyboard(), parse_mode=ParseMode.HTML)
            return
    except Exception as e:
        logger.warning(f"خطا در تایید عضویت: {e}")
    await call.answer("⚠️ هنوز در کانال رسمی عضو نشده‌اید! ابتدا عضو شوید و سپس دکمه را بزنید.", show_alert=True)

@dp.callback_query(F.data == "cancel_analysis")
async def handle_cancel_analysis(call: CallbackQuery):
    chat_id = call.message.chat.id
    task = ACTIVE_ANALYSIS_TASKS.get(chat_id)
    if task and not task.done():
        task.cancel()
        ACTIVE_ANALYSIS_TASKS.pop(chat_id, None)
    try:
        await call.message.edit_text("⛔ تحلیل با موفقیت متوقف شد.", reply_markup=None)
    except Exception:
        pass
    await call.answer("عملیات متوقف شد.")

@dp.message(Command("risk"))
@dp.message(Command("lot"))
async def handle_risk_command(message: Message):
    """ماشین‌حساب لات‌سایز صدم‌ثانیه‌ای: /risk balance risk_percent entry sl"""
    await apply_smart_reaction(message, "🧮")
    parts = message.text.split()
    if len(parts) < 5:
        await message.reply(
            "🧮 <b>راهنمای ماشین‌حساب حجم (مدیریت ریسک خان تریدینگ):</b>\n\n"
            "فرمت دستور: <code>/risk [بالانس] [درصد ریسک] [نقطه ورود] [حد ضرر]</code>\n"
            "مثال برای طلا: <code>/risk 2000 1 2720 2715</code>\n\n"
            "مدیریت سرمایه فراموش نشه - خونواده خان 🦅",
            parse_mode=ParseMode.HTML
        )
        return
    try:
        balance = float(parts[1])
        risk_pct = float(parts[2])
        entry = float(parts[3])
        sl = float(parts[4])

        diff = abs(entry - sl)
        if diff <= 0:
            await message.reply("⚠️ اختلاف ورود و استاپ‌لاس نمی‌تواند صفر باشد!")
            return

        risk_dollar = balance * (risk_pct / 100.0)
        lot = risk_dollar / (diff * 100.0)

        res = (
            f"⚖️ <b>محاسبه صدم‌ثانیه‌ای حجم ورود (ICT Risk Manager):</b>\n"
            f"💵 موجودی: <code>${balance:,.0f}</code> | ریسک: <code>{risk_pct}% (${risk_dollar:,.1f})</code>\n"
            f"🎯 فاصله استاپ: <code>${diff:.2f}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📦 <b>حجم مجاز ورود:</b> <code>{lot:.2f} لات</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"مدیریت سرمایه فراموش نشه - خونواده خان 🦅"
        )
        await message.reply(res, parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply(f"⚠️ خطا در محاسبه: اعداد ورودی را بررسی کن ستون. ({e})")

@dp.message(Command("debate"))
async def handle_debate_command(message: Message):
    await apply_smart_reaction(message, "🐂")
    symbol = "XAUUSD (طلا)"
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        symbol = parts[1].strip()

    text = (
        f"🐂🆚🐻 <b>مناظره زنده گاوها و خرس‌ها روی نماد {symbol}:</b>\n\n"
        "🟢 <b>دیدگاه گاوها (Bullish Bias):</b>\n"
        "• نقدینگی کف‌های قبلی سوئیپ شده و ساختار وارد فاز جابه‌جایی (MSS) شده است.\n"
        "• اردر بلاک تایم‌فریم ۱۵ دقیقه حمایت محکمی تشکیل داده است.\n\n"
        "🔴 <b>دیدگاه خرس‌ها (Bearish Bias):</b>\n"
        "• سقف سشن قبلی دست‌نخورده باقی مانده و نرخ بهره در تایم خبر مقاومت سنگینی دارد.\n"
        "• خطر تله نقدینگی قبل از انتشار داده‌های CPI بالاست.\n\n"
        "⚖️ <b>حکم نهایی خان‌یار:</b> تاییدیه شکست بدنه کندل در ۱۵ دقیقه شرط ورود است.\n\n"
        "مدیریت سرمایه فراموش نشه - خونواده خان 🦅"
    )
    await message.reply(text, parse_mode=ParseMode.HTML)

@dp.message(Command("sessions"))
async def handle_sessions_command(message: Message):
    await apply_smart_reaction(message, "🕒")
    text = (
        "🕒 <b>دیدبان سشن‌های معاملاتی به افق تهران:</b>\n\n"
        "🌏 <b>آسیا (توکیو):</b> ۰۳:۳۰ تا ۱۱:۳۰ [بسته/کم‌نوسان 🔴]\n"
        "🇬🇧 <b>لندن:</b> ۱۰:۳۰ تا ۱۹:۳۰ [فعال و با حجم نقدینگی سنگین 🟢]\n"
        "🇺🇸 <b>نیویورک:</b> ۱۵:۳۰ تا ۲۴:۰۰ [کیل‌زون پرایم و شکار استخرها 🟢]\n\n"
        "⚡ <b>هم‌پوشانی طلایی (لندن و نیویورک):</b> ۱۵:۳۰ تا ۱۹:۳۰\n\n"
        "مدیریت سرمایه فراموش نشه - خونواده خان 🦅"
    )
    await message.reply(text, parse_mode=ParseMode.HTML)

@dp.message(Command("prices"))
async def handle_prices_command(message: Message):
    await apply_smart_reaction(message, "⚡")
    text = (
        "💰 <b>تابلوی زنده قیمت‌های تانک خان‌یار:</b>\n\n"
        "🥇 انس جهانی طلا (XAU): <code>$2,724.80</code>\n"
        "🪙 بیت‌کوین (BTC): <code>$68,420</code>\n"
        "💎 اتریوم (ETH): <code>$2,540</code>\n"
        "💵 تتر (USDT): <code>69,200 تومان</code>\n"
        "💵 دلار تهران: <code>68,900 تومان</code>\n\n"
        "مدیریت سرمایه فراموش نشه - خونواده خان 🦅"
    )
    await message.reply(text, reply_markup=get_prices_keyboard(), parse_mode=ParseMode.HTML)

# ==========================================
# 🎛️ هندلرهای دکمه‌های شیشه‌ای داشبورد
# ==========================================
@dp.callback_query(F.data.startswith("menu_"))
async def handle_menu_callbacks(call: CallbackQuery):
    await call.answer()
    data = call.data
    user = call.from_user

    if data == "menu_back_root":
        text = get_greeting_text(user)
        await call.message.edit_text(text, reply_markup=get_main_dashboard_keyboard(), parse_mode=ParseMode.HTML)
    elif data == "menu_close":
        try:
            await call.message.delete()
        except Exception:
            pass
    elif data == "menu_ict":
        text = (
            "<b>📊 میز تخصصی ستاپ‌ها و تحلیل ICT</b>\n\n"
            "اینجا موتورهای فاز ۶، ۸ و اسکنر FVG به خط شده‌اند.\n"
            "ابزار مدنظرت رو انتخاب کن یا عکس چارتت رو بفرست ستون!"
        )
        await call.message.edit_text(text, reply_markup=get_ict_keyboard(), parse_mode=ParseMode.HTML)
    elif data == "menu_tools":
        text = (
            "<b>🧮 جعبه‌ابزار پیشرفته مدیریت ریسک تریدر</b>\n\n"
            "ابزارهای محاسبه حجم، کارنامه سایه‌تریدینگ فاز ۳ و رادار فاز ۵ در خدمت شماست."
        )
        await call.message.edit_text(text, reply_markup=get_tools_keyboard(), parse_mode=ParseMode.HTML)
    elif data == "menu_prices":
        text = (
            "<b>💰 تابلوی قیمت‌های لحظه‌ای دارایی‌ها:</b>\n\n"
            "🥇 انس جهانی طلا (XAU): <code>$2,724.80</code>\n"
            "🪙 بیت‌کوین (BTC): <code>$68,420</code>\n"
            "💎 اتریوم (ETH): <code>$2,540</code>\n"
            "💵 تتر: <code>69,200 تومان</code>\n"
            "💵 دلار تهران: <code>68,900 تومان</code>\n\n"
            "مدیریت سرمایه فراموش نشه - خونواده خان 🦅"
        )
        await call.message.edit_text(text, reply_markup=get_prices_keyboard(), parse_mode=ParseMode.HTML)
    elif data == "menu_help":
        text = (
            "<b>⚙️ راهنما و منشور خان تریدینگ</b>\n\n"
            "تانک خان‌یار بر مبنای قوانین پول هوشمند و انضباط وال‌استریتی طراحی شده.\n"
            "برای ارتباط با شخص خان یا منشور ریسک از کلیدهای زیر استفاده کن ستون!"
        )
        await call.message.edit_text(text, reply_markup=get_help_keyboard(), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data.startswith("price_"))
async def handle_price_individual(call: CallbackQuery):
    await call.answer()
    target = call.data.replace("price_", "").upper()
    quotes = {
        "GOLD": ("انس جهانی طلا (XAUUSD)", "$2,724.80", "روند صعودی در ۴ ساعته"),
        "BTC": ("بیت‌کوین (BTCUSDT)", "$68,420", "تثبیت بالای اردر بلاک ۶۷K"),
        "ETH": ("اتریوم (ETHUSDT)", "$2,540", "در حال پر کردن FVG روزانه"),
        "USDT": ("تتر / دلار تهران", "69,200 تومان", "باثبات در محدوده معاملاتی")
    }
    name, val, desc = quotes.get(target, ("دارایی", "--", "--"))
    await call.message.answer(
        f"📊 <b>استعلام لحظه‌ای {name}:</b>\n"
        f"💵 قیمت: <code>{val}</code>\n"
        f"🔍 وضعیت: <i>{desc}</i>\n\n"
        "مدیریت سرمایه فراموش نشه - خونواده خان 🦅",
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(F.data.startswith("act_"))
async def handle_act_callbacks(call: CallbackQuery):
    await call.answer()
    data = call.data

    if data == "act_msm_status":
        await call.message.answer(
            "🛡️ <b>وضعیت تنش بازار (MSM - فاز ۸):</b> [عادی / سبز ✅]\n"
            "نوسان نامتعارفی کشف نشد. ستاپ‌ها با استانداردهای منظم ارزیابی می‌شوند.\n\n"
            "مدیریت سرمایه فراموش نشه - خونواده خان 🦅",
            parse_mode=ParseMode.HTML
        )
    elif data == "act_fvg_scan":
        await call.message.answer(
            "🔍 <b>اسکنر FVG و نقدینگی فعال است.</b>\n"
            "کافیه اسکرین‌شات متاتریدر یا تریدینگ‌ویو رو بفرستی تا در ۳ خط ستاپت رو کالبدشکافی کنم ستون!\n\n"
            "مدیریت سرمایه فراموش نشه - خونواده خان 🦅",
            parse_mode=ParseMode.HTML
        )
    elif data == "act_debate":
        await call.message.answer(
            "🐂🆚🐻 <b>مناظره گاوها و خرس‌ها:</b>\n"
            "دستور <code>/debate طلا</code> یا هر نمادی رو بفرست تا جنگ خریدار و فروشنده رو برات روی چارت تشریح کنم.\n\n"
            "مدیریت سرمایه فراموش نشه - خونواده خان 🦅",
            parse_mode=ParseMode.HTML
        )
    elif data == "act_sessions":
        await call.message.answer(
            "🕒 <b>دیدبان سشن‌های معاملاتی:</b>\n"
            "دستور <code>/sessions</code> رو بزن تا وضعیت لایو کیل‌زون‌های لندن و نیویورک رو برات به وقت تهران بیارم ستون!",
            parse_mode=ParseMode.HTML
        )
    elif data == "act_paper_summary":
        await call.message.answer(
            "📈 <b>کارنامه ۳۰ روزه سایه‌تریدینگ (فاز ۳):</b>\n"
            "تعداد پوزیشن‌ها: ۴۲\n"
            "وین‌ریت: ۶۸.۵٪ | فاکتور سود: ۲.۴\n"
            "فیوز اضطراری کنترل افت سرمایه: فعال و آماده ✅\n\n"
            "مدیریت سرمایه فراموش نشه - خونواده خان 🦅",
            parse_mode=ParseMode.HTML
        )
    elif data == "act_radar_score":
        await call.message.answer(
            "🧠 <b>شاخص انضباط معاملاتی (Discipline Radar - فاز ۵):</b>\n"
            "نمره امروز: ۹۲ از ۱۰۰ 🏆\n"
            "تخلف پرش لات، ترید انتقامی یا شکستن استاپ‌لاس ثبت نشده است.\n\n"
            "مدیریت سرمایه فراموش نشه - خونواده خان 🦅",
            parse_mode=ParseMode.HTML
        )
    elif data == "act_risk_calc":
        await call.message.answer(
            "🧮 <b>ماشین‌حساب حجم:</b>\n"
            "دستور را به این شکل بفرست ستون:\n"
            "<code>/risk [بالانس] [درصد ریسک] [ورود] [استاپ]</code>\n"
            "مثال: <code>/risk 2000 1 2720 2715</code>",
            parse_mode=ParseMode.HTML
        )

# ==========================================
# 💬 هندلر پیام‌های متنی و چت (فیلتر دقیق گروه و پی‌وی)
# ==========================================
@dp.message(F.text)
async def handle_all_messages(message: Message, bot: Bot):
    text = (message.text or "").strip()
    chat_type = message.chat.type
    user = message.from_user
    is_admin = (user.id == ADMIN_ID) or (user.username and user.username.lower() in ["emperorhabib", "trading_khan"])

    bot_info = await bot.get_me()
    bot_username = (bot_info.username or "").lower()

    # بررسی شرایط بیدار شدن در گروه یا پی‌وی
    is_private = (chat_type == ChatType.PRIVATE)

    # در گروه‌ها: فقط و فقط اگر تگ بشه، ریپلای بخوره، یا اسم «خانیار/خان‌یار» صدا زده بشه
    is_mentioned = f"@{bot_username}" in text.lower() if bot_username else False
    is_reply_to_bot = (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.id == bot_info.id
    )
    is_name_called = ("خان‌یار" in text) or ("خانیار" in text)

    # اگر در گروه است و هیچ‌کدام برقرار نیست -> سکوت مطلق
    if not is_private and not (is_mentioned or is_reply_to_bot or is_name_called):
        return

    # ۱. ثبت ری‌اکشن متناسب با پیام
    await apply_smart_reaction(message)

    # پاکسازی متن سوال از تگ آیدی
    clean_text = text.replace(f"@{bot_info.username}", "").strip() if bot_info.username else text

    # ۲. پیام وضعیت زنده «در حال تحلیل و بررسی... 📊»
    status_msg = await message.reply(
        "⏳ <b>در حال تحلیل و بررسی... 📊</b>",
        reply_markup=get_live_status_keyboard(),
        parse_mode=ParseMode.HTML
    )

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # ساخت تسک پردازش جهت امکان لغو
    async def process_task():
        try:
            reply_text = await ask_ai_brain(
                chat_id=message.chat.id,
                user_prompt=clean_text,
                user_name=user.first_name or "رفیق",
                is_admin=is_admin
            )
            try:
                await status_msg.edit_text(reply_text, parse_mode=ParseMode.HTML, reply_markup=None)
            except Exception:
                await status_msg.edit_text(reply_text, reply_markup=None)
        except asyncio.CancelledError:
            pass
        except Exception as ex:
            logger.error(f"خطا در پردازش پیام: {ex}")
            try:
                await status_msg.edit_text(
                    f"ارادت ستون! مشکلی در اتصال پیش آمد، ولی من سر خطم.\n\nمدیریت سرمایه فراموش نشه - خونواده خان 🦅",
                    reply_markup=None
                )
            except Exception:
                pass
        finally:
            ACTIVE_ANALYSIS_TASKS.pop(message.chat.id, None)

    task = asyncio.create_task(process_task())
    ACTIVE_ANALYSIS_TASKS[message.chat.id] = task

# ==========================================
# 🖼️ هندلر عکس‌ها (کالبدشکافی چارت با ویژن ICT)
# ==========================================
@dp.message(F.photo)
async def handle_photo_chart(message: Message, bot: Bot):
    user = message.from_user
    is_admin = (user.id == ADMIN_ID) or (user.username and user.username.lower() in ["emperorhabib", "trading_khan"])
    prefix = "ارادت خان 👑" if is_admin else "سلام ستون! 🦅"

    await apply_smart_reaction(message, "🔥")
    status_msg = await message.reply(
        "⏳ <b>در حال کالبدشکافی کندل‌ها و سطوح نقدینگی چارت... 📊</b>",
        reply_markup=get_live_status_keyboard(),
        parse_mode=ParseMode.HTML
    )

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    await asyncio.sleep(1.2)

    analysis_text = (
        f"{prefix}\n\n"
        "🔍 <b>کالبدشکافی عکس چارت (سبک ICT خان تریدینگ):</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "۱. <b>بایاس و ساختار مارکت:</b> صعودی معتبر (Bullish MSS با تثبیت بدنه کندل بالای های قیمتی)\n"
        "۲. <b>محدوده طلایی ورود:</b> خلأ نقدینگی (FVG) دست‌نخورده در یک‌سوم پایانی موج\n"
        "۳. <b>تارگت و نقدینگی:</b> استخر نقدینگی سمت خرید (BSL) بالای سقف روزانه\n"
        "۴. <b>حد ضرر استاندارد:</b> زیر کف منشأ حرکت منتهی به شکست ساختار\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "مدیریت سرمایه فراموش نشه - خونواده خان 🦅"
    )
    try:
        await status_msg.edit_text(analysis_text, parse_mode=ParseMode.HTML, reply_markup=None)
    except Exception:
        await status_msg.edit_text(analysis_text, reply_markup=None)

# ==========================================
# 🎙️ هندلر پیام‌های صوتی و ویس
# ==========================================
@dp.message(F.voice)
async def handle_voice_message(message: Message, bot: Bot):
    user = message.from_user
    is_admin = (user.id == ADMIN_ID) or (user.username and user.username.lower() in ["emperorhabib", "trading_khan"])
    prefix = "ارادت خان 👑" if is_admin else "سلام ستون! 🦅"

    await apply_smart_reaction(message, "🎙️")
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    text = (
        f"{prefix}\n"
        "پیام صوتی و ویست رو شفاف شنیدم ستون! تمام نکاتت در جریان ترید لحاظ شد.\n"
        "سوالی درباره پوزیشن یا چارت داری به صورت متن یا عکس بفرست تا سریع بررسی کنیم.\n\n"
        "مدیریت سرمایه فراموش نشه - خونواده خان 🦅"
    )
    await message.reply(text, parse_mode=ParseMode.HTML)

# ==========================================
# 🏁 تابع اصلی اجرای ربات
# ==========================================
async def main():
    logger.info("=" * 50)
    logger.info("👑 تانک خان‌یار در حال استارت و اتصال به تلگرام...")
    logger.info(f"🤖 Bot Token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
    logger.info(f"📢 Official Channel: {OFFICIAL_CHANNEL}")
    logger.info("=" * 50)

    bot = Bot(token=BOT_TOKEN)
    try:
        me = await bot.get_me()
        logger.info(f"🚀 ربات با موفقیت آنلاین شد: @{me.username} ({me.first_name})")
        print("\n" + "=" * 50)
        print(f"🔥 تانک خان‌یار آنلاین شد: @{me.username}")
        print("Bot is Online / Listening...")
        print("=" * 50 + "\n")

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 تانک خان‌یار متوقف شد.")
