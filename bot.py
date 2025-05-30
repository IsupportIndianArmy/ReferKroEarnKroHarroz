import telebot
import sqlite3

BOT_TOKEN = '8162907304:AAEzeqxRP8lCFxzY8tj-3HdySxvNXAJd3i4'
bot = telebot.TeleBot(BOT_TOKEN)

# Database setup
conn = sqlite3.connect('referbot.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    referred_by INTEGER,
    points INTEGER DEFAULT 0
)
''')
conn.commit()

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or f"user{user_id}"
    args = message.text.split()

    referred_by = None
    if len(args) > 1:
        try:
            referred_by = int(args[1])
        except:
            pass

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (user_id, username, referred_by) VALUES (?, ?, ?)",
                       (user_id, username, referred_by))
        if referred_by:
            cursor.execute("UPDATE users SET points = points + 1 WHERE user_id = ?", (referred_by,))
        conn.commit()

    bot.send_message(user_id, f"Welcome, {username}!")

"bot.send_message(user_id, f"Hello, {username}!")
                              f"🔗 Your referral link:
"
                              f"https://t.me/YOUR_BOT_USERNAME?start={user_id}")

# /points command
@bot.message_handler(commands=['points'])
def points(message):
    user_id = message.from_user.id
    cursor.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    points = result[0] if result else 0
    bot.send_message(user_id, f"💰 You have {points} referral point(s)!")

bot.polling()
