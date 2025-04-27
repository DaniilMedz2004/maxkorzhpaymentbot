
import os
import logging
from telebot import TeleBot, types

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Read token from environment
token = os.environ.get("TELEGRAM_TOKEN")
if not token:
    logging.error("Environment variable TELEGRAM_TOKEN is missing. Exiting.")
    raise SystemExit("Error: TELEGRAM_TOKEN is not set")

# Initialize bot
bot = TeleBot(token)
print("🐍 Bot is starting…", flush=True)

# Bot settings
wallet_address = "TEz82XF79p1UbkXgzHiimfskyJGjrEXXWg"
ticket_price = 110.66
user_data = {}

languages = {
    'pl': 'Polski',
    'ru': 'Русский',
    'en': 'English',
    'ua': 'Українська'
}

payment_texts = {
    'pl': "Aby dokonać płatności, przekaż {amount:.2f} USDT (TRC-20)\n\nPortfel:\n{wallet}",
    'ru': "Для оплаты переведите {amount:.2f} USDT (TRC-20)\n\nКошелек:\n{wallet}",
    'en': "To make a payment, send {amount:.2f} USDT (TRC-20)\n\nWallet:\n{wallet}",
    'ua': "Для оплати перекиньте {amount:.2f} USDT (TRC-20)\n\nГаманець:\n{wallet}"
}

# Helper functions

def send_language_selection(chat_id, reply_to_message_id=None):
    markup = types.InlineKeyboardMarkup()
    for code, name in languages.items():
        markup.add(types.InlineKeyboardButton(text=name, callback_data=code))
    bot.send_message(chat_id, "Select your language / Выберите язык / Wybierz język / Виберіть мову:",
                     reply_markup=markup, reply_to_message_id=reply_to_message_id)

# Handlers

@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    logging.info(f"Received /start from {message.from_user.username} ({chat_id})")
    user_data[chat_id] = {}
    send_language_selection(chat_id)

@bot.callback_query_handler(func=lambda call: call.data in languages.keys())
def language_selected(call):
    chat_id = call.message.chat.id
    selected_lang = call.data
    user_data[chat_id]['lang'] = selected_lang
    logging.info(f"User {chat_id} selected language: {selected_lang}")
    text = payment_texts[selected_lang].format(amount=ticket_price, wallet=wallet_address)
    markup = types.InlineKeyboardMarkup(
        [[types.InlineKeyboardButton(text="Paid / Оплачено", callback_data='paid'),
          types.InlineKeyboardButton(text="Back / Назад", callback_data='back')]]
    )
    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=text,
                          reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ['paid', 'back'])
def callback_buttons(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data == 'paid':
        logging.info(f"User {chat_id} clicked Paid")
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text="Проверяем оплату... (Пока тестовый ответ)")
    elif call.data == 'back':
        logging.info(f"User {chat_id} clicked Back")
        send_language_selection(chat_id, reply_to_message_id=message_id)

# Start polling
if __name__ == '__main__':
    bot.polling(none_stop=True)
