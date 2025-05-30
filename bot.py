{\rtf1\ansi\ansicpg1252\deff0\nouicompat{\fonttbl{\f0\fnil\fcharset0 Calibri;}{\f1\fnil Calibri;}{\f2\fnil\fcharset1 Segoe UI Symbol;}{\f3\fnil\fcharset1 Segoe UI Symbol;}}
{\colortbl ;\red0\green0\blue255;}
{\*\generator Riched20 10.0.19041}\viewkind4\uc1 
\pard\sa200\sl276\slmult1\f0\fs22\lang9 # (Full code \f1\emdash  this combines both the referral logic and channel check)\par
\par
import logging\par
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup\par
from telegram.ext import (\par
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,\par
    ContextTypes, MessageHandler, filters\par
)\par
from datetime import datetime, timedelta\par
import os\par
\par
# Enable logging\par
logging.basicConfig(level=logging.INFO)\par
logger = logging.getLogger(__name__)\par
\par
# Constants\par
CHANNEL_USERNAME = "@RIyL8z1mZPMxNDVl"  # Join-check channel\par
CHANNEL_INVITE_LINK = "{{\field{\*\fldinst{HYPERLINK https://t.me/+RIyL8z1mZPMxNDVl }}{\fldrslt{https://t.me/+RIyL8z1mZPMxNDVl\ul0\cf0}}}}\f1\fs22 "\par
REFERRAL_REWARD = 6\par
DAILY_BONUS = 2\par
WITHDRAWAL_MINIMUM = 100\par
\par
# In-memory storage\par
users = \{\}\par
\par
# Util: get or initialize user data\par
def get_user(user_id):\par
    if user_id not in users:\par
        users[user_id] = \{\par
            'balance': 0,\par
            'referrals': 0,\par
            'joined': datetime.now(),\par
            'last_bonus': None,\par
            'referred_by': None,\par
            'has_joined_channel': False\par
        \}\par
    return users[user_id]\par
\par
# UI: 2x2 Inline Keyboard Layout\par
def main_menu():\par
    keyboard = [\par
        [InlineKeyboardButton("\f2\u-10179?\u-9040?\f0  Balance", callback_data='balance'),\par
         InlineKeyboardButton("\f2\u-10179?\u-8988?\f0  Withdraw", callback_data='withdraw')],\par
        [InlineKeyboardButton("\f2\u-10179?\u-8990?\f0  Referral Info", callback_data='referral'),\par
         InlineKeyboardButton("\f2\u-10179?\u-9000?\f0  How to Earn?", callback_data='howto')],\par
    ]\par
    return InlineKeyboardMarkup(keyboard)\par
\par
def back_button():\par
    return InlineKeyboardMarkup([[InlineKeyboardButton("\f2\u-10179?\u-8935?\f0  Back", callback_data='back')]])\par
\par
# Join Channel Check\par
async def is_user_in_channel(user_id, context):\par
    try:\par
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)\par
        return member.status in ['member', 'administrator', 'creator']\par
    except Exception as e:\par
        logger.warning(f"Channel check failed: \{e\}")\par
        return False\par
\par
# /start command\par
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):\par
    user = update.effective_user\par
    user_id = user.id\par
    user_data = get_user(user_id)\par
\par
    # Referral system\par
    if context.args:\par
        referrer_id = int(context.args[0])\par
        if referrer_id != user_id and not user_data['referred_by']:\par
            referrer_data = get_user(referrer_id)\par
            referrer_data['balance'] += REFERRAL_REWARD\par
            referrer_data['referrals'] += 1\par
            user_data['referred_by'] = referrer_id\par
\par
    # Check channel membership\par
    if not await is_user_in_channel(user_id, context):\par
        join_keyboard = InlineKeyboardMarkup([\par
            [InlineKeyboardButton("\f3\u9989?\f0  Join Channel", url=CHANNEL_INVITE_LINK)],\par
            [InlineKeyboardButton("\f2\u-10179?\u-8956?\f0  I've Joined", callback_data="verify_join")]\par
        ])\par
        await update.message.reply_text(\par
            "\f2\u-10179?\u-8944?\f0  To use the bot, please join our official channel first:",\par
            reply_markup=join_keyboard\par
        )\par
        return\par
\par
    # Proceed to main menu\par
    await update.message.reply_text(\par
        f"\f2\u-10179?\u-9141?\f0  Welcome \{user.first_name\}!\\nUse the buttons below to start earning:",\par
        reply_markup=main_menu()\par
    )\par
\par
# Join Verification\par
async def verify_join(update: Update, context: ContextTypes.DEFAULT_TYPE):\par
    query = update.callback_query\par
    user_id = query.from_user.id\par
\par
    if await is_user_in_channel(user_id, context):\par
        await query.edit_message_text("\f3\u9989?\f0  Verified! Welcome.", reply_markup=main_menu())\par
    else:\par
        await query.edit_message_text("\f3\u10060?\f0  You still haven't joined. Please join the channel first.",\par
                                      reply_markup=InlineKeyboardMarkup([\par
                                          [InlineKeyboardButton("\f3\u9989?\f0  Join Channel", url=CHANNEL_INVITE_LINK)],\par
                                          [InlineKeyboardButton("\f2\u-10179?\u-8956?\f0  I've Joined", callback_data="verify_join")]\par
                                      ]))\par
\par
# CallbackHandler\par
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):\par
    query = update.callback_query\par
    user_id = query.from_user.id\par
    user_data = get_user(user_id)\par
    await query.answer()\par
\par
    if query.data == "balance":\par
        msg = f"\f2\u-10179?\u-9032?\f0  Balance: \u8377?\{user_data['balance']\}\\n\f2\u-10179?\u-9115?\f0  Referrals: \{user_data['referrals']\}"\par
        await query.edit_message_text(msg, reply_markup=back_button())\par
\par
    elif query.data == "withdraw":\par
        if user_data['balance'] >= WITHDRAWAL_MINIMUM:\par
            await query.edit_message_text(\par
                f"\f3\u9989?\f0  Withdrawal request of \u8377?\{user_data['balance']\} received.\\nWe'll contact you shortly.",\par
                reply_markup=back_button()\par
            )\par
            user_data['balance'] = 0\par
        else:\par
            await query.edit_message_text(\par
                f"\f3\u10060?\f0  Minimum \u8377?\{WITHDRAWAL_MINIMUM\} required to withdraw.\\nYour balance: \u8377?\{user_data['balance']\}",\par
                reply_markup=back_button()\par
            )\par
\par
    elif query.data == "referral":\par
        bot_username = context.bot.username\par
        referral_link = f"https://t.me/\{bot_username\}?start=\{user_id\}"\par
        msg = f"\f2\u-10179?\u-8990?\f0  Share this link and earn \u8377?6 per referral:\\n\{referral_link\}"\par
        await query.edit_message_text(msg, reply_markup=back_button())\par
\par
    elif query.data == "howto":\par
        msg = (\par
            "\f2\u-10179?\u-9000?\f0  *How to Earn:*\\n\\n"\par
            "1. Join the required channel\\n"\par
            "2. Share your referral link with friends\\n"\par
            "3. Earn \u8377?6 per valid referral\\n"\par
            "4. Withdraw at \u8377?100 minimum"\par
        )\par
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=back_button())\par
\par
    elif query.data == "back":\par
        await query.edit_message_text("\f2\u-10179?\u-8935?\f0  Back to main menu:", reply_markup=main_menu())\par
\par
# Unknown messages\par
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):\par
    await update.message.reply_text("\f3\u10067?\f0  Use /start or tap buttons to interact with the bot.")\par
\par
# Main app\par
def main():\par
    TOKEN = os.getenv("8162907304:AAEzeqxRP8lCFxzY8tj-3HdySxvNXAJd3i4")  # Secure token loading\par
\par
    app = ApplicationBuilder().token(TOKEN).build()\par
\par
    app.add_handler(CommandHandler("start", start))\par
    app.add_handler(CallbackQueryHandler(handle_callback))\par
    app.add_handler(CallbackQueryHandler(verify_join, pattern="^verify_join$"))\par
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))\par
\par
    logger.info("Bot is running...")\par
    app.run_polling()\par
\par
if __name__ == "__main__":\par
    main()\par
}
 