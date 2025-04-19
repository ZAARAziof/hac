import requests
import logging
import json
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
ADMIN_ID = 7711640688
TOKEN = "7428090451:AAFFyoGcoYaQsE6CA9-rizZ6GPO4Yvv-Nkw"
DEMO_DURATION = timedelta(minutes=5)  # 5 minutes demo
USER_DATA_FILE = "user_data.json"
DEMO_NOTICE = "⚠️ *Note:* You are using Demo Version (5 minutes). Contact admin @Z44R4_exploit for full access"
API_URL = "https://dev-pycodz-blackbox.pantheonsite.io/DEvZ44d/Hacker.php"
API_KEY = "pysx--A1b2C3d4E5F6g7H8I9J"

class HackerGpt:
    def __init__(self):
        self.url = API_URL
        self.api_key = API_KEY
        self.session = requests.Session()

    def prompt(self, request):
        json_data = {
            "text": request,
            "api_key": self.api_key
        }
        try:
            response = self.session.post(url=self.url, json=json_data, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return "🔧 Server is currently busy. Please try again later."

# User management functions
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading user data: {e}")
    return {"users": {}, "admin": ADMIN_ID}

def save_user_data(data):
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        logger.error(f"Error saving user data: {e}")

user_data = load_user_data()

def is_admin(user_id):
    return user_id == user_data["admin"]

def is_authorized(user_id):
    if is_admin(user_id):
        return True
    user_info = user_data["users"].get(str(user_id))
    if not user_info:
        return False
    try:
        expiry = datetime.fromisoformat(user_info["expiry"])
        return datetime.now() < expiry
    except (ValueError, KeyError) as e:
        logger.error(f"Error checking authorization: {e}")
        return False

def has_used_demo(user_id):
    return str(user_id) in user_data["users"]

def add_demo_user(user_id):
    expiry = datetime.now() + DEMO_DURATION
    user_data["users"][str(user_id)] = {
        "expiry": expiry.isoformat(),
        "is_demo": True
    }
    save_user_data(user_data)
    return expiry

def format_time_remaining(expiry):
    try:
        remaining = expiry - datetime.now()
        if remaining.total_seconds() <= 0:
            return "expired"
        
        minutes = int(remaining.total_seconds() / 60)
        seconds = int(remaining.total_seconds() % 60)
        return f"{minutes} minutes {seconds} seconds"
    except Exception as e:
        logger.error(f"Error formatting time: {e}")
        return "unknown"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_admin(user_id):
        welcome_msg = """
👑 *Welcome Admin!* 👑

You have full premium access to HackerGPT.

Send me any question or command and I'll respond like a hacker.☠
"""
    elif is_authorized(user_id):
        user_info = user_data["users"][str(user_id)]
        expiry = datetime.fromisoformat(user_info["expiry"])
        time_left = format_time_remaining(expiry)
        welcome_msg = f"""
🔹 *Demo Access Active* 🔹

⏳ *Time remaining:* {time_left}

{DEMO_NOTICE}
"""
    else:
        welcome_msg = """
🔒 *Access Denied* 🔒

You don't have access to HackerGPT.

Contact admin @Z44R4_exploit to get full access.

Try our free 5-minute demo with /demo
"""
    
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")

async def demo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_admin(user_id):
        await update.message.reply_text("👑 Admin doesn't need demo access!")
        return
    
    if is_authorized(user_id):
        await update.message.reply_text("ℹ️ You already have an active session.")
        return
    
    if has_used_demo(user_id):
        await update.message.reply_text("❌ You've already used your demo access. Contact admin @Z44R4_exploit for full access.")
        return
    
    expiry = add_demo_user(user_id)
    time_left = format_time_remaining(expiry)
    
    response = f"""
🎉 *Demo Access Granted!* 🎉

⏳ *Duration:* 5 minutes
⏱ *Time remaining:* {time_left}

{DEMO_NOTICE}
"""
    await update.message.reply_text(response, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_admin(user_id):
        await update.message.reply_text("👑 You are admin with full premium access!")
        return
    
    if not is_authorized(user_id):
        await update.message.reply_text("🔒 You don't have an active session. Try /demo for free access.")
        return
    
    user_info = user_data["users"][str(user_id)]
    expiry = datetime.fromisoformat(user_info["expiry"])
    time_left = format_time_remaining(expiry)
    
    response = f"""
🔹 *Demo Session Info* 🔹

⏳ *Time remaining:* {time_left}
📅 *Expires at:* {expiry.strftime('%Y-%m-%d %H:%M')}

{DEMO_NOTICE}
"""
    await update.message.reply_text(response, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    help_text = """
ℹ️ *HackerGPT Help* ℹ️

Available commands:

/start - Show welcome message
/help - Show this help message
/demo - Get 5-minute free trial
/status - Check your demo status
"""
    if is_admin(user_id):
        help_text += "\n👑 *Admin Commands:*\n/admin - Admin panel (coming soon)"
    
    help_text += "\n\nContact @Z44R4_exploit for support"
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if not is_authorized(user_id):
        await update.message.reply_text(
            "🔒 You don't have access. Try /demo for free trial or contact admin @Z44R4_exploit.",
            parse_mode="Markdown"
        )
        return
    
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    try:
        response = HackerGpt().prompt(user_message)
        
        # Clean the response to avoid Markdown issues
        response = response.replace("*", "").replace("_", "").replace("`", "")
        
        if not is_admin(user_id):
            response = f"{response}\n\n{DEMO_NOTICE}"
        
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await update.message.reply_text(
            "❌ An error occurred while processing your request. Please try again.",
            parse_mode="Markdown"
        )

def main():
    """Start the bot."""
    try:
        application = Application.builder().token(TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("demo", demo_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        logger.info("Starting bot...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")

if __name__ == '__main__':
    main()
