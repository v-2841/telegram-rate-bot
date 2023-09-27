import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters


load_dotenv()
Path('data/').mkdir(exist_ok=True)


async def rates(update, context):
    chat = update.effective_chat
    url_template = ('https://cdn.jsdelivr.net/gh/fawazahmed0/'
                    + 'currency-api@1/latest/currencies/{}/{}.json')
    in_progress = await context.bot.send_message(
        chat_id=chat.id,
        text=('Загружаю данные...\n□□□□□□□'),
    )
    rates = {}

    url = url_template.format('usd', 'rub')
    response = requests.get(url)

    # Проверяем доступ к серверу
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

    # Проверяем status code
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

    # Проверяем, что поля соответстуют ожиданию
    if 'rub' not in data.keys():
        await context.bot.delete_message(
            chat_id=chat.id,
            message_id=in_progress.message_id,
        )
        await context.bot.send_message(
            chat_id=chat.id,
            text=('Неожиданный ответ стороннего сервера'),
        )
        return

    # Проверяем наличие кэшированных данных
    if os.path.isfile(f'data/{data["date"]}.txt'):
        await context.bot.delete_message(
            chat_id=chat.id,
            message_id=in_progress.message_id,
        )
        with open(f'data/{data["date"]}.txt', 'r') as file:
            await context.bot.send_message(
                chat_id=chat.id,
                text=(file.read()),
            )
        return

    # Если данных нет, то загружаем их
    rates['Дата'] = str(data['date']) + '\n'
    rates['Доллар -> Рубль'] = data['rub']
    await context.bot.edit_message_text(
        text=('Загружаю данные...\n■□□□□□□'),
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )

    url = url_template.format('eur', 'rub')
    response = requests.get(url)
    data = response.json()
    rates['Евро -> Рубль'] = str(data['rub']) + '\n'
    await context.bot.edit_message_text(
        text=('Загружаю данные...\n■■□□□□□'),
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )

    url = url_template.format('eur', 'usd')
    response = requests.get(url)
    data = response.json()
    rates['Евро -> Доллар'] = str(data['usd']) + '\n'
    await context.bot.edit_message_text(
        text=('Загружаю данные...\n■■■□□□□'),
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )

    url = url_template.format('amd', 'rub')
    response = requests.get(url)
    data = response.json()
    rates['Драм -> Рубль'] = data['rub']
    await context.bot.edit_message_text(
        text=('Загружаю данные...\n■■■■□□□'),
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )

    url = url_template.format('rub', 'amd')
    response = requests.get(url)
    data = response.json()
    rates['Рубль -> Драм'] = str(data['amd']) + '\n'
    await context.bot.edit_message_text(
        text=('Загружаю данные...\n■■■■■□□'),
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )

    url = url_template.format('eur', 'amd')
    response = requests.get(url)
    data = response.json()
    rates['Евро -> Драм'] = data['amd']
    await context.bot.edit_message_text(
        text=('Загружаю данные...\n■■■■■■□'),
        chat_id=chat.id,
        message_id=in_progress.message_id,
    )

    url = url_template.format('usd', 'amd')
    response = requests.get(url)
    data = response.json()
    rates['Доллар -> Драм'] = data['amd']
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
    with open(f'data/{data["date"]}.txt', 'w') as file:
        file.write(rates_text)


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
