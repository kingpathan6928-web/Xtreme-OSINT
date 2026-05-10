import logging
import re
import requests
import html
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIG ---
BOT_TOKEN = "8729580730:AAGTgZwLyBI4Pe7oeayMDYsrtZ8i6jcPgxM"
PHOTO_URL = "https://i.postimg.cc/7YmD0hj0/IMG-20260510-134258.png"
CHANNEL_ID = "@infohub_salman" 
YT_LINK = "https://youtube.com/@infohub_salman"
BASE_API_URL = "https://har-har-mahadev-psi.vercel.app/api?key=FREE_ME_11_DAY&number="

logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO)

# --- HELPERS ---
def escape_md(text):
    """MarkdownV2 ke liye special characters ko escape karta hai"""
    if not text: return "N/A"
    # In characters ko escape karna zaroori hai
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', str(text))

# --- KEYBOARDS ---
def main_menu_kb():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🔍 Available Services")],
        [KeyboardButton("💰 My Credits"), KeyboardButton("🆔 My ID")],
        [KeyboardButton("💳 Buy Credits"), KeyboardButton("🤝 Refer & Earn")],
        [KeyboardButton("🎁 Gift Codes")]
    ], resize_keyboard=True)

def services_menu_kb():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🇮🇳 India Number"), KeyboardButton("🇵🇰 Pakistan Number")],
        [KeyboardButton("🪪 Aadhar Card"), KeyboardButton("📍 Pincode")],
        [KeyboardButton("🚘 Vehicle Info"), KeyboardButton("🎯 Number Tracker")],
        [KeyboardButton("🔙 Back to Main")]
    ], resize_keyboard=True)

# --- JOIN CHECK LOGIC ---
async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# --- START / VERIFICATION SCREEN ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not await is_subscribed(update, context):
        text = (
            f"👋 *Hey {escape_md(user.first_name)}*\\!\n\n"
            "⚠️ *Access Locked\\!*\n"
            "Bot use karne ke liye niche diye gaye dono steps poore karein:\n\n"
            "1️⃣ Telegram Channel join karein\\.\n"
            "2️⃣ YouTube Channel subscribe karein\\."
        )
        kb = [
            [InlineKeyboardButton("📢 Join Telegram", url=f"https://t.me/infohub_salman")],
            [InlineKeyboardButton("📺 Subscribe YouTube", url=YT_LINK)],
            [InlineKeyboardButton("✅ Verified / Tap to Start", callback_data="check_status")]
        ]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="MarkdownV2")
        return
    
    welcome = (
        f"🌟 *WELCOME TO XTREME OSINT\\!*\n\n"
        f"👤 *User:* {escape_md(user.first_name)}\n"
        f"🆔 *ID:* `{user.id}`\n"
        f"✅ *Status:* Fully Verified\n"
        f"🎁 *Free Credits:* 5"
    )
    await update.message.reply_photo(photo=PHOTO_URL, caption=welcome, reply_markup=main_menu_kb(), parse_mode="MarkdownV2")

# --- MESSAGE HANDLER ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await start(update, context)
        return

    text = update.message.text
    user = update.effective_user

    if text == "🔍 Available Services":
        await update.message.reply_text("🔍 *SELECT YOUR SERVICE:*", reply_markup=services_menu_kb(), parse_mode="MarkdownV2")
    
    elif text == "🔙 Back to Main":
        await update.message.reply_text("👋 *Returning to Main Menu\\.\\.\\.*", reply_markup=main_menu_kb(), parse_mode="MarkdownV2")

    elif text == "🆔 My ID":
        info = (
            "🆔 *YOUR PROFILE INFO*\n"
            "____________________________________\n\n"
            f"📝 *Name:* {escape_md(user.first_name)}\n"
            f"🆔 *User ID:* `{user.id}`\n"
            f"🌐 *Username:* @{escape_md(user.username) if user.username else 'N/A'}\n"
            f"📅 *Joined Bot:* Verified\n"
            "____________________________________"
        )
        await update.message.reply_text(info, parse_mode="MarkdownV2")

    elif text == "💰 My Credits":
        await update.message.reply_text("💰 *BALANCE INFO*\n\n💎 *Available Credits:* 5\n🌟 *Plan:* Free Tier", parse_mode="MarkdownV2")

    elif text == "💳 Buy Credits":
        await update.message.reply_text("💳 *RECHARGE CREDITS*\n\nContact Admin for instant credits:\n👉 @infohub\\_salman\n\n*Rate:* ₹10 \\= 100 Credits", parse_mode="MarkdownV2")

    elif text == "🤝 Refer & Earn":
        bot_me = await context.bot.get_me()
        bot_username = bot_me.username
        ref_link = f"https://t\\.me/{bot_username}?start={user.id}"
        msg = (
            "🤝 *REFER & EARN PROGRAM*\n\n"
            "Apne doston ko invite karein aur har successful refer par *5 Credits* payein\\!\n\n"
            f"🔗 *Your Referral Link:*\n{ref_link}"
        )
        await update.message.reply_text(msg, parse_mode="MarkdownV2")

    elif text == "🎁 Gift Codes":
        await update.message.reply_text("🎁 *REDEEM GIFT CODE*\n\nCode enter karein \\(e\\.g\\. `SALMAN100`\\):\n\n_Note: Abhi koi active code nahi hai\\._", parse_mode="MarkdownV2")

    elif text == "🇮🇳 India Number":
        await update.message.reply_text("📩 *SEND NUMBER NOW:*\nExample: `9507310448`", parse_mode="MarkdownV2")

    elif text.isdigit() and len(text) >= 10:
        loading = await update.message.reply_text("🔎 *Searching Live Database\\.\\.\\.*", parse_mode="MarkdownV2")
        try:
            response = requests.get(f"{BASE_API_URL}{text}", timeout=30)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if results:
                    res = results[0]
                    # Data ko safe banake display karna
                    name = escape_md(res.get('name'))
                    addr = escape_md(res.get('address'))
                    circle = escape_md(res.get('circle'))
                    
                    full_info = (
                        "✅ *DATA FOUND*\n"
                        "____________________________________\n\n"
                        f"📱 *Mobile:* `{text}`\n"
                        f"👤 *Name:* `{name}`\n"
                        f"🏠 *Address:* `{addr}`\n"
                        f"🌐 *Circle:* `{circle}`\n"
                        "____________________________________\n\n"
                        "📡 *Status:* Verified Database"
                    )
                else:
                    full_info = "⚠️ *Status:* No record found for this number\\."
            else:
                full_info = "❌ *API Error:* Server response failed\\."
        except Exception:
            full_info = "❌ *Connection Error:* Timeout\\."
        
        await loading.edit_text(full_info, parse_mode="MarkdownV2")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Bot is LIVE with Formatting Fixes!")
    application = app
    application.run_polling()

if __name__ == "__main__":
    main()
    
