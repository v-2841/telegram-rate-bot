import os

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters


load_dotenv()


async def rates(update, context):
    chat = update.effective_chat
    in_progress = await context.bot.send_message(
        chat_id=chat.id,
        text=('Загружаю данные...\n□□□□□□□'),
    )
    rates = {}

    url = 'https://api.exchangerate.host/convert?from=USD&to=RUB'
    try:
        response = requests.get(url)
    except Exception:
        await context.bot.delete_message(
            chat_id=chat.id,
            message_id=in_progress.message_id,
        )
        await context.bot.send_message(
            chat_id=chat.id,
            text=('Ошибка доступа к стороннему серверу'),
        )
        return

    if response.status_code != 200:
        await context.bot.delete_message(
            chat_id=chat.id,
            message_id=in_progress.message_id,
        )
        await context.bot.send_message(
            chat_id=chat.id,
            text=('Ошибка на стороннем сервере '
                  + f'{response.status_code} {response.reason}'),
        )
        return

    data = response.json()
    if 'result' not in data.keys():
        await context.bot.delete_message(
            chat_id=chat.id,
            message_id=in_progress.message_id,
        )
        await context.bot.send_message(
            chat_id=chat.id,
            text=('Неожиданный ответ стороннего сервера'),
        )
        return

    rates['Дата'] = str(data['date']) + '\n'
    rates['Доллар -> Рубль'] = data['result']
    await context.bot.edit_message_text(
        text=('Загружаю данные...\n■□□□□□□'),
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )

    url = 'https://api.exchangerate.host/convert?from=EUR&to=RUB'
    response = requests.get(url)
    data = response.json()
    rates['Евро -> Рубль'] = str(data['result']) + '\n'
    await context.bot.edit_message_text(
        text=('Загружаю данные...\n■■□□□□□'),
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )

    url = 'https://api.exchangerate.host/convert?from=EUR&to=USD'
    response = requests.get(url)
    data = response.json()
    rates['Евро -> Доллар'] = str(data['result']) + '\n'
    await context.bot.edit_message_text(
        text=('Загружаю данные...\n■■■□□□□'),
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )

    url = 'https://api.exchangerate.host/convert?from=AMD&to=RUB'
    response = requests.get(url)
    data = response.json()
    rates['Драм -> Рубль'] = data['result']
    await context.bot.edit_message_text(
        text=('Загружаю данные...\n■■■■□□□'),
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )

    url = 'https://api.exchangerate.host/convert?from=RUB&to=AMD'
    response = requests.get(url)
    data = response.json()
    rates['Рубль -> Драм'] = str(data['result']) + '\n'
    await context.bot.edit_message_text(
        text=('Загружаю данные...\n■■■■■□□'),
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )

    url = 'https://api.exchangerate.host/convert?from=EUR&to=AMD'
    response = requests.get(url)
    data = response.json()
    rates['Евро -> Драм'] = data['result']
    await context.bot.edit_message_text(
        text=('Загружаю данные...\n■■■■■■□'),
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )

    url = 'https://api.exchangerate.host/convert?from=USD&to=AMD'
    response = requests.get(url)
    data = response.json()
    rates['Доллар -> Драм'] = data['result']
    await context.bot.edit_message_text(
        text=('Загружаю данные...\n■■■■■■■'),
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )

    rates_text = ''
    for key in rates:
        rates_text += f'{key}: {rates[key]}\n'
    await context.bot.delete_message(
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )
    await context.bot.send_message(
        chat_id=chat.id,
        text=(rates_text),
    )


async def wake_up(update, context):
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([
                ['Курс на сегодня']
            ], resize_keyboard=True)
    await context.bot.send_message(
        chat_id=chat.id,
        text=('Привет!'),
        reply_markup=buttons,
    )


if __name__ == '__main__':
    application = Application.builder().token(
        os.getenv('TELEGRAM_TOKEN', 'token')).build()
    application.add_handler(CommandHandler('start', wake_up))
    application.add_handler(MessageHandler(
        filters.Regex('^Курс на сегодня$'), rates))
    application.run_polling(allowed_updates=Update.ALL_TYPES)
