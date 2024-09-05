import logging
import os
import time
from flask import Flask
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from threading import Thread

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your bot token
TOKEN = '7417326600:AAH9gwQ-Leygnt3u6fv8MEdEnB-1B4bWgKQ'
CHANNEL_ID = '-1002192323521'

# Sticker IDs
stickers_start = [
    'CAACAgUAAxkBAAMlZtW0o720ihUo1Q_i9TNKWKs0k2wAAh0DAAIX8Dw_q5ta8w_YR5A1BA',
    'CAACAgUAAxkBAAMdZtW0bJjy9sXJYXVbdZdUe5uQUI4AAgkMAAK9mqlXC7p6g6hG8Go1BA',
    'CAACAgUAAxkBAAMfZtW0b5zd50z4HEQUr-EMbltjsNYAAhgDAAIX8Dw_7cRJz4SNqao1BA',
    'CAACAgUAAxkBAAMtZtW2hQyQzauUqxVPhbUhhzOvjXEAAvsKAAIWG_BWlMq--iOTVBE1BA'
]

stickers_win = [
    'CAACAgUAAxkBAAMZZtW0VvwcBdSsfBiqRD88Lpn8OAsAAskMAALxrqhXiE6elcPOq_I1BA',
    'CAACAgUAAxkBAAMhZtW0cJHzkefnm_gyzPXFBDdo0VUAAusCAAIX8Dw_3_LhmE7ofq81BA'
]

stickers_win1 = [
    'CAACAgUAAxkBAAMbZtW0WpB6RBPk9W405sYf9nfApHAAAtUMAAJboKlXS_k3N6RQTVc1BA',
    'CAACAgUAAxkBAAMhZtW0cJHzkefnm_gyzPXFBDdo0VUAAusCAAIX8Dw_3_LhmE7ofq81BA'
]

stickers_win2 = [
    'CAACAgUAAxkBAAMjZtW0ke8So0A2am0IdmYMgiMON-AAApERAAICHLBWgV2_WJyNaxU1BA',
    'CAACAgUAAxkBAAMhZtW0cJHzkefnm_gyzPXFBDdo0VUAAusCAAIX8Dw_3_LhmE7ofq81BA'
]

stickers_loss = [
    'CAACAgUAAxkBAAMjZtW0ke8So0A2am0IdmYMgiMON-AAApERAAICHLBWgV2_WJyNaxU1BA',
    'CAACAgUAAxkBAAMhZtW0cJHzkefnm_gyzPXFBDdo0VUAAusCAAIX8Dw_3_LhmE7ofq81BA'
]

# Update ID tracking
def get_last_update_id():
    if os.path.exists('last_update_id.txt'):
        with open('last_update_id.txt', 'r') as f:
            return int(f.read())
    return 0

def set_last_update_id(update_id):
    with open('last_update_id.txt', 'w') as f:
        f.write(str(update_id))

# Debounce configuration
last_processed_time = 0
debounce_interval = 2  # seconds

async def start(update: Update, context: CallbackContext) -> None:
    for sticker in stickers_start:
        await context.bot.send_sticker(chat_id=CHANNEL_ID, sticker=sticker)

async def handle_channel_message(update: Update, context: CallbackContext) -> None:
    global last_processed_time
    current_time = time.time()

    if current_time - last_processed_time < debounce_interval:
        logger.info("Debounced update, ignoring")
        return

    last_processed_time = current_time

    if update.channel_post is None:
        logger.info("Received update with no channel post")
        return

    update_id = update.update_id
    last_update_id = get_last_update_id()

    if update_id <= last_update_id:
        logger.info(f"Update {update_id} already processed")
        return

    text = update.channel_post.text
    logger.info(f"Received channel message: {text}")

    # Define sticker list based on message text
    sticker_list = []
    if text == 'WIN ✅':
        sticker_list = stickers_win
    elif text == 'WIN ✅¹':
        sticker_list = stickers_win1
    elif text == 'WIN ✅²':
        sticker_list = stickers_win2
    elif text == '💔 Loss':
        sticker_list = stickers_loss

    # Send stickers only once per message
    if sticker_list:
        for sticker in sticker_list:
            await context.bot.send_sticker(chat_id=CHANNEL_ID, sticker=sticker)

    # Mark this update as processed
    set_last_update_id(update_id)

# Function to run the bot
def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_channel_message))
    application.run_polling()

# Create a simple Flask app for port binding
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# Start Flask app in a separate thread
def start_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Run Flask app in a separate thread
    Thread(target=start_flask).start()
    # Run the bot
    run_bot()
