import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from aiohttp import ClientSession
from dotenv import load_dotenv
from peewee_async import Manager, PostgresqlDatabase
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from models import Message, User


load_dotenv()

db = PostgresqlDatabase(
    os.getenv('POSTGRES_DB', 'bot_rates'),
    user=os.getenv('POSTGRES_USER', 'user'),
    password=os.getenv('POSTGRES_PASSWORD', ''),
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', 5432),
)

Path('logs/').mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(name)s, %(levelname)s, %(funcName)s, %(message)s',
    handlers=[RotatingFileHandler(
        'logs/main.log', maxBytes=100000, backupCount=10)],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

pairs = [
    ['eur', 'usd'],
    ['usd', 'rub'],
    ['eur', 'rub'],
    ['amd', 'rub'],
    ['rub', 'amd'],
    ['usd', 'amd'],
    ['eur', 'amd'],
]
translation = {
    'usd': 'Доллар',
    'eur': 'Евро',
    'rub': 'Рубль',
    'amd': 'Драм',
}
url_template = ('https://cdn.jsdelivr.net/gh/fawazahmed0/'
                + 'currency-api@1/latest/currencies/{}/{}.json')


async def get_date(client):
    url = url_template.format(*pairs[0])
    async with client.get(url) as response:
        data = await response.json()
        return f'Дата: {data["date"]}'


async def get_rate(client, pair):
    async with client.get(url=url_template.format(*pair)) as response:
        data = await response.json()
        return (f'{translation[pair[0]]} -> {translation[pair[1]]}: '
                + f'{data[pair[1]]}')


async def rates(update, context):
    chat = update.effective_chat
    await application.bot_data['objects'].create(
        Message,
        id=update.message.message_id,
        from_user=chat.id,
        to_user=0,
        text=update.message.text,
    )
    tasks = [asyncio.create_task(get_date(context.bot_data['client']))]
    for pair in pairs:
        tasks.append(asyncio.create_task(
            get_rate(context.bot_data['client'], pair)))
    rates = await asyncio.gather(*tasks)
    rates_text = '\n'.join(rates)
    message = await context.bot.send_message(
        chat_id=chat.id,
        text=(rates_text),
    )
    logger.info(f'Пользователь {chat.id} запросил курс')
    await application.bot_data['objects'].create(
        Message,
        id=message.message_id,
        from_user=0,
        to_user=chat.id,
        text=rates_text,
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
    logger.info(f'Пользователь {chat.id} включил бота')
    await application.bot_data['objects'].create_or_get(User, id=chat.id)


async def post_init(application: Application) -> None:
    application.bot_data['client'] = ClientSession()
    logger.info('Клиент ClientSession запущен')
    application.bot_data['objects'] = Manager(db)
    application.bot_data['objects'].database.allow_sync = logging.ERROR
    logger.info('База данных присоединена')


async def post_shutdown(application: Application) -> None:
    await application.bot_data['client'].close()
    logger.info('Клиент ClientSession остановлен')
    await application.bot_data['objects'].close()
    logger.info('База данных отсоединена')


if __name__ == '__main__':
    application = Application.builder().token(
        os.getenv('TELEGRAM_TOKEN', 'token')).post_init(
            post_init).post_shutdown(post_shutdown).build()
    application.add_handler(CommandHandler('start', wake_up))
    application.add_handler(MessageHandler(
        filters.Regex('^Курс на сегодня$'), rates))
    application.run_polling()
