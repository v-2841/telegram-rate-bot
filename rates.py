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

url_template = ('https://cdn.jsdelivr.net/npm/@fawazahmed0/'
                + 'currency-api@latest/v1/currencies/{}.json')
currencies = ['eur', 'usd', 'rub', 'amd']
rates_message = ('Курсы валют на {date} 💸\n\n'
                 + 'Евро 🇪🇺 -> Доллар 🇺🇸: {eur_usd}\n\n'
                 + 'Доллар 🇺🇸 -> Рубль 🇷🇺: {usd_rub}\n'
                 + 'Евро 🇪🇺 -> Рубль 🇷🇺: {eur_rub}\n\n'
                 + 'Драм 🇦🇲 -> Рубль 🇷🇺: {amd_rub}\n'
                 + 'Рубль 🇷🇺 -> Драм 🇦🇲: {rub_amd}\n\n'
                 + 'Доллар 🇺🇸 -> Драм 🇦🇲: {usd_amd}\n'
                 + 'Евро 🇪🇺 -> Драм 🇦🇲: {eur_amd}'
                 )


async def get_date(client):
    url = url_template.format(currencies[0])
    async with client.get(url) as response:
        data = await response.json()
        return {'date': data["date"]}


async def get_currency_rates(client, currency):
    async with client.get(url=url_template.format(currency)) as response:
        data = await response.json()
        return {f'{currency}': data[currency]}


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
    for currency in currencies:
        tasks.append(asyncio.create_task(
            get_currency_rates(context.bot_data['client'], currency)))
    rates = await asyncio.gather(*tasks)
    dict_rates = {}
    for _ in rates:
        dict_rates.update(_)
    rates_text = rates_message.format(
        date=dict_rates['date'],
        eur_usd=dict_rates['eur']['usd'],
        usd_rub=dict_rates['usd']['rub'],
        eur_rub=dict_rates['eur']['rub'],
        amd_rub=dict_rates['amd']['rub'],
        rub_amd=dict_rates['rub']['amd'],
        usd_amd=dict_rates['usd']['amd'],
        eur_amd=dict_rates['eur']['amd'],
    )
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
