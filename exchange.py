import os

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater


load_dotenv()
updater = Updater(token=os.getenv('TELEGRAM_TOKEN_EXCHANGE', 'token'))


def rates(update, context):
    chat = update.effective_chat
    rates = {}

    url = 'https://api.exchangerate.host/convert?from=USD&to=RUB'
    response = requests.get(url)
    data = response.json()
    rates['Дата'] = str(data['date']) + '\n'
    rates['Доллар -> Рубль'] = data['result']

    url = 'https://api.exchangerate.host/convert?from=EUR&to=RUB'
    response = requests.get(url)
    data = response.json()
    rates['Евро -> Рубль'] = str(data['result']) + '\n'

    url = 'https://api.exchangerate.host/convert?from=EUR&to=USD'
    response = requests.get(url)
    data = response.json()
    rates['Евро -> Доллар'] = str(data['result']) + '\n'

    url = 'https://api.exchangerate.host/convert?from=AMD&to=RUB'
    response = requests.get(url)
    data = response.json()
    rates['Драм -> Рубль'] = data['result']

    url = 'https://api.exchangerate.host/convert?from=RUB&to=AMD'
    response = requests.get(url)
    data = response.json()
    rates['Рубль -> Драм'] = str(data['result']) + '\n'

    url = 'https://api.exchangerate.host/convert?from=EUR&to=AMD'
    response = requests.get(url)
    data = response.json()
    rates['Евро -> Драм'] = data['result']

    url = 'https://api.exchangerate.host/convert?from=USD&to=AMD'
    response = requests.get(url)
    data = response.json()
    rates['Доллар -> Драм'] = data['result']

    rates_text = ''
    for key in rates:
        rates_text += f'{key}: {rates[key]}\n'
    context.bot.send_message(
        chat_id=chat.id,
        text=(rates_text),
    )


def wake_up(update, context):
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([
                ['/rates']
            ], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text=('Привет!'),
        reply_markup=buttons,
    )


updater.dispatcher.add_handler(CommandHandler('start', wake_up))
updater.dispatcher.add_handler(CommandHandler('rates', rates))
updater.start_polling()
updater.idle()
