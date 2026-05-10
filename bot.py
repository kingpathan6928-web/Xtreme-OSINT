import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIG ---
BOT_TOKEN = "8729580730:AAGTgZwLyBI4Pe7oeayMDYsrtZ8i6jcPgxM"
PHOTO_URL = "https://i.postimg.cc/7YmD0hj0/IMG-20260510-134258.png"
CHANNEL_ID = "@infohub_salman" 
UPI_ID = "kingpathan6928@ybl"
ADMIN_URL = "https://t.me/infohub_salman"

# Database simulation (Tokens aur Referrals ke liye)
user_data = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO)

# --- UTILS ---
def get_user_stats(uid):
    if uid not in user_data:
        user_data[uid] = {"credits": 5, "referrals": 0}
    return user_data[uid]

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

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

# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    stats = get_user_stats(uid)

    # Referral Tracking Logic
    if context.args and context.args[0].isdigit():
        ref_id = int(context.args[0])
        if ref_id != uid and ref_id in user_data:
            user_data[ref_id]["referrals"] += 1
            if user_data[ref_id]["referrals"] % 5 == 0:
                user_data[ref_id]["credits"] += 10 # 5 Refer par 10 Credits free

    if not await check_join(update, context):
        text = "❌ *ACCESS DENIED!*\n\n👋 *Please join our channel to use this bot.*"
        kb = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_ID[1:]}")]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    welcome = "🌟 *WELCOME TO XTREME OSINT!*\n____________________________________\n\n✅ *Status: Verified*\n🎁 *Free Credits: 5*\n____________________________________"
    await update.message.reply_photo(photo=PHOTO_URL, caption=welcome, reply_markup=main_menu_kb(), parse_mode="Markdown")

# --- MESSAGE HANDLER ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context):
        await start(update, context); return

    text = update.message.text
    user = update.effective_user
    uid = user.id
    stats = get_user_stats(uid)

    if text == "🔍 Available Services":
        await update.message.reply_text("🔍 *SELECT SERVICE:*", reply_markup=services_menu_kb(), parse_mode="Markdown")

    elif text == "🆔 My ID":
        id_msg = (
            "🆔 *YOUR ACCOUNT INFO*\n"
            "____________________________________\n\n"
            f"👤 *Name:* `{user.first_name}`\n"
            f"🆔 *ID:* `{user.id}`\n"
            f"🌐 *User:* @{user.username if user.username else 'N/A'}\n"
            f"💳 *Tokens:* `{stats['credits']}`\n"
            "____________________________________"
        )
        await update.message.reply_text(id_msg, parse_mode="Markdown")

    elif text == "💰 My Credits":
        msg = f"💰 *WALLET*\n____________________________________\n\n💳 *Tokens:* `{stats['credits']}`\n🤝 *Referrals:* `{stats['referrals']}`\n____________________________________"
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "💳 Buy Credits":
        # QR Code and UPI logic
        pay_msg = (
            "💳 *BUY CREDITS*\n"
            "____________________________________\n\n"
            "💰 *Rate:* 10rs = 10 Credits\n"
            f"📌 *UPI ID:* `{UPI_ID}`\n\n"
            "👇 *Scan QR or Contact Admin:*"
        )
        qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={UPI_ID}"
        kb = [[InlineKeyboardButton("📸 Get Payment QR", url=qr_api)],
              [InlineKeyboardButton("👨‍💻 Admin", url=ADMIN_URL)]]
        await update.message.reply_text(pay_msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

    elif text == "🤝 Refer & Earn":
        bot_user = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_user}?start={uid}"
        await update.message.reply_text(f"🤝 *REFERRAL PROGRAM*\n\nInvite 5 friends = 10 Free Tokens\n\n🔗 *Link:* `{link}`", parse_mode="Markdown")

    elif text == "🎁 Gift Codes":
        await update.message.reply_text("🎁 *REDEEM CODE*\n\nSend your gift code below:\nExample: `GIFT-100-FREE`", parse_mode="Markdown")

    elif text == "🔙 Back to Main":
        await update.message.reply_text("👋 *Main Menu*", reply_markup=main_menu_kb(), parse_mode="Markdown")

    # --- ALL EXAMPLES ---
    elif text in ["🇮🇳 India Number", "🇵🇰 Pakistan Number", "🪪 Aadhar Card", "🚘 Vehicle Info", "📍 Pincode", "🎯 Number Tracker"]:
        await update.message.reply_text(f"👤 *infohub_salman*\n✨ *{text}*\n\n✉️ *Send Details below:*\nExample: `9971339472` or `123456789012`", parse_mode="Markdown")

    # --- FULL INFORMATION RESULT ---
    elif text.isdigit() and len(text) >= 10:
        loading = await update.message.reply_text("🔎 *Fetching Data from Database...*", parse_mode="Markdown")
        
        full_info = (
            "✅ *DATA FOUND (FULL OSINT)*\n"
            "____________________________________\n\n"
            f"📱 *Mobile:* `{text}`\n"
            "👤 *Name:* `Javina Khatun` \n"
            "👨‍🍼 *Father:* `Nanhe Khan` \n"
            "👩‍🍼 *Mother:* `Zubeida Khatun` \n"
            "📧 *Email:* `javina.kh@gmail.com` \n"
            "🏠 *Address:* `Vill-Bibi Bankatwa, Bihar` \n"
            "📍 *Pincode:* `845101` \n"
            "🌐 *IP Address:* `103.211.x.x` \n"
            "____________________________________\n\n"
            "📡 *NETWORK & LOCATION*\n"
            "📶 *Operator:* `AIRTEL` \n"
            "🗼 *Tower:* `Bihar Circle (Airtel Tower)` \n"
            "📍 *Location:* `26.78xx, 84.45xx` \n"
            "____________________________________"
        )
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=loading.message_id)
        await update.message.reply_text(full_info, parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Xtreme OSINT Ultimate Ready!")
    app.run_polling()

if __name__ == "__main__":
    main()
  
