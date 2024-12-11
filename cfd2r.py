import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, JobQueue
from telegram.ext import ApplicationBuilder, Job

TELEGRAM_BOT_TOKEN = "CREATE YOUR OWN BOT"
TARGET_PRICE = 34.99
PRODUCT_URL = "https://eu.shop.battle.net/en-gb/product/diablo_ii_resurrected"

def get_current_price():
    response = requests.get(PRODUCT_URL)
    response.raise_for_status() 
    price_start = response.text.find('"price":')
    if price_start == -1:
        return None
    price_data = response.text[price_start:price_start + 50]
    price_str = price_data.split(':')[1].strip().strip('"').split(',')[0]
    cleaned_price = ''.join(char for char in price_str if char.isdigit() or char == '.')
    return float(cleaned_price) if cleaned_price else None
async def check_price(update: Update, context: CallbackContext):
    try:
        current_price = get_current_price()
        if current_price is not None:
            if current_price < TARGET_PRICE:
                message = f"The price has dropped to £{current_price}!"
            else:
                message = f"Current price is still £{current_price}."
        else:
            message = "Couldn't fetch the price."
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def check_price_periodically(application: Application):
    async def job(context: CallbackContext):
        chat_id = "ADD YOUR BOT'S CHAT ID" 
        current_price = get_current_price()
        
        if current_price is not None:
            if current_price < TARGET_PRICE:
                message = f"The price has dropped to £{current_price}!"
                await application.bot.send_message(chat_id=chat_id, text=message)
            else:
                message = f"Current price is still £{current_price}."
                await application.bot.send_message(chat_id=chat_id, text=message)
        else:
            await application.bot.send_message(chat_id=chat_id, text="Couldn't fetch the price.")
    job_queue = application.job_queue
    job_queue.run_repeating(job, interval=86400, first=0)

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("check", check_price)) 
    check_price_periodically(application)
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
