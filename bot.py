
import telebot
from telebot import types

TOKEN = '7336019242:AAEdQXgUvPg0D3bjL-YAkj7ICzOWTNWqJD4'
bot = telebot.TeleBot(TOKEN)

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
    'en': "To pay, transfer {amount:.2f} USDT (TRC-20)\n\nWallet:\n{wallet}",
    'ua': "Щоб оплатити, переказуйте {amount:.2f} USDT (TRC-20)\n\nГаманець:\n{wallet}"
}

paid_texts = {
    'pl': "Opłaciłem",
    'ru': "Оплатил",
    'en': "Paid",
    'ua': "Сплатив"
}

back_texts = {
    'pl': "Wróć",
    'ru': "Назад",
    'en': "Back",
    'ua': "Назад"
}

@bot.message_handler(commands=['start'])
def start_message(message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith('bilety_'):
        try:
            ticket_count = int(args[1].split('_')[1])
            user_data[message.chat.id] = {'tickets': ticket_count}
            send_language_selection(message.chat.id)
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "Ошибка в параметре билетов.")
    else:
        bot.send_message(message.chat.id, "Добро пожаловать! Пожалуйста, выберите билеты сначала на сайте.")

def send_language_selection(chat_id, message_id=None):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for code, lang_name in languages.items():
        markup.add(types.InlineKeyboardButton(text=lang_name, callback_data=f"lang_{code}"))
    
    text = "Выберите язык / Choose language / Wybierz język / Оберіть мову:"
    
    if message_id:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

def send_payment_info(chat_id, message_id=None):
    ticket_count = user_data.get(chat_id, {}).get('tickets', 1)
    selected_lang = user_data.get(chat_id, {}).get('language', 'ru')
    total_amount = ticket_price * ticket_count

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_paid = types.InlineKeyboardButton(text=paid_texts[selected_lang], callback_data='paid')
    btn_back = types.InlineKeyboardButton(text=back_texts[selected_lang], callback_data='back')
    markup.add(btn_paid, btn_back)

    payment_message = payment_texts[selected_lang].format(amount=total_amount, wallet=wallet_address)

    if message_id:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=payment_message, reply_markup=markup)
    else:
        bot.send_message(chat_id, payment_message, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def callback_language(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    selected_lang = call.data.split('_')[1]

    if chat_id in user_data:
        user_data[chat_id]['language'] = selected_lang
        send_payment_info(chat_id, message_id=message_id)
    else:
        bot.send_message(chat_id, "Ошибка: билеты не выбраны.")

@bot.callback_query_handler(func=lambda call: call.data in ['paid', 'back'])
def callback_buttons(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == 'paid':
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Проверяем оплату... (Пока тестовый ответ)")
    elif call.data == 'back':
        send_language_selection(chat_id, message_id=message_id)

bot.polling(none_stop=True)
