import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- FLASK SERVER (Render Port Error ለመፍታት) ---
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT CONFIGURATION ---
BOT_TOKEN = "7721959290:AAHrCNY2GVQUSdhObfL3hCGeU6yeQFCw0OA"
CHANNEL_USERNAME = "@MTsibeb"
ADMIN_ID = 7341220208
PHOTO_URL = "https://picsum.photos/800/400"

async def is_user_subscribed(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    subscribed = await is_user_subscribed(context.bot, user_id)

    if not subscribed:
        keyboard = [
            [InlineKeyboardButton("📢 ቻናላችንን ይቀላቀሉ", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("✅ ተቀላቅያለሁ (Check)", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"ሰላም {first_name}! 👋\n\n⚠️ ቦቱን ለመጠቀም አስቀድመው የቴሌግራም ቻናላችንን መቀላቀል አለብዎት።",
            reply_markup=reply_markup
        )
        return

    keyboard = [
        [
            InlineKeyboardButton("ስለ ቦቱ ℹ️", callback_data="about"),
            InlineKeyboardButton("እርዳታ ❓", callback_data="help")
        ],
        [
            InlineKeyboardButton("📢 ዋና ቻናል", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"),
            InlineKeyboardButton("🔗 ሁለተኛ ቻናል", url="https://t.me/ethio_konjo1")
        ],
        [
            InlineKeyboardButton("💬 አስተያየት/መልእክት ላክ", callback_data="send_feedback")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption_text = f"✨ **እንኳን ደህና መጡ {first_name}!** ✨\n\nከታች ያሉትን አዝራሮች በመጫን የሚፈልጉትን አገልግሎት ያግኙ።"
    
    await update.message.reply_photo(
        photo=PHOTO_URL,
        caption=caption_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "check_subscription":
        subscribed = await is_user_subscribed(context.bot, user_id)
        if subscribed:
            await query.message.reply_text("✅ እናመሰግናለን! ቻናሉን ተቀላቅለዋል። አሁን /start በማለት ቦቱን መጠቀም ይችላሉ።")
        else:
            await query.answer("❌ አሁንም ቻናሉን አልተቀላቀሉም! እባክዎን አስቀድመው Join ያድርጉ።", show_alert=True)

    elif query.data == "about":
        await query.message.reply_text(text="🚀 **ስለ ቦቱ**\n\nይህ በ Python የታገዘ ዘመናዊ የቴሌግራም ቦት ነው።", parse_mode="Markdown")
    
    elif query.data == "help":
        await query.message.reply_text(text="❓ **እርዳታ**\n\nቦቱን ለመጠቀም ወይም አስተያየት ለመስጠት 'አስተያየት/መልእክት ላክ' የሚለውን አዝራር ይጠቀሙ።", parse_mode="Markdown")

    elif query.data == "send_feedback":
        context.user_data['waiting_for_feedback'] = True
        await query.message.reply_text("✍️ **እባክዎን አስተያየትዎን ወይም መልእክትዎን አሁን ይፃፉልን፦**")

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_feedback'):
        user_text = update.message.text
        user = update.effective_user
        
        admin_message = (
            f"📩 **አዲስ አስተያየት ተልኳል!**\n\n"
            f"👤 **ላኪ፦** {user.first_name} (@{user.username})\n"
            f"🆔 **ID፦** `{user.id}`\n\n"
            f"💬 **መልእክት፦**\n{user_text}"
        )
        
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, parse_mode="Markdown")
            await update.message.reply_text("✅ መልእክትዎ በትክክል ደርሶናል! እናመሰግናለን።")
        except Exception:
            await update.message.reply_text("✅ መልእክትዎ ተቀብለናል! እናመሰግናለን።")
            
        context.user_data['waiting_for_feedback'] = False

if __name__ == '__main__':
    # 1. አስቀድሞ Flask ሰርቨሩን ማስነሳት
    keep_alive()
    
    # 2. ቦቱን ማስነሳት
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback))

    print("ቦቱ መስራት ጀምሯል...")
    app.run_polling()
