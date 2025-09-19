import logging
import os
from datetime import datetime

from aiohttp import ClientSession
from telegram import ReplyKeyboardMarkup
from telegram.ext import (AIORateLimiter, Application, CommandHandler,
                          MessageHandler, filters)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

URL_TEMPLATE = ('https://openexchangerates.org/api/latest.json'
                + f'?app_id={os.getenv("API_TOKEN")}&symbols=RUB%2CEUR%2CAMD')
RATES_MESSAGE = ('Курсы валют на {date} UTC 💸\n\n'
                 + 'Евро 🇪🇺 -> Доллар 🇺🇸: {eur_usd}\n\n'
                 + 'Доллар 🇺🇸 -> Рубль 🇷🇺: {usd_rub}\n'
                 + 'Евро 🇪🇺 -> Рубль 🇷🇺: {eur_rub}\n\n'
                 + 'Драм 🇦🇲 -> Рубль 🇷🇺: {amd_rub}\n'
                 + 'Рубль 🇷🇺 -> Драм 🇦🇲: {rub_amd}\n\n'
                 + 'Доллар 🇺🇸 -> Драм 🇦🇲: {usd_amd}\n'
                 + 'Евро 🇪🇺 -> Драм 🇦🇲: {eur_amd}'
                 )


async def rates(update, context):
    chat = update.effective_chat
    logger.info(f'Пользователь {chat.id} запросил курс')
    async with context.bot_data['client'].get(url=URL_TEMPLATE) as response:
        data = await response.json()
    timestamp = datetime.fromtimestamp(data['timestamp'])
    rates = data['rates']
    rates_text = RATES_MESSAGE.format(
        date=timestamp,
        eur_usd=f"{round(1/rates['EUR'], 3):.3f}",
        usd_rub=f"{round(rates['RUB'], 2):.2f}",
        eur_rub=f"{round(rates['RUB']/rates['EUR'], 2):.2f}",
        amd_rub=f"{round(rates['AMD']/rates['RUB'], 3):.3f}",
        rub_amd=f"{round(rates['RUB']/rates['AMD'], 4):.4f}",
        usd_amd=f"{round(rates['AMD'], 2):.2f}",
        eur_amd=f"{round(rates['AMD']/rates['EUR'], 2):.2f}",
    )
    await context.bot.send_message(
        chat_id=chat.id,
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


async def post_init(application: Application) -> None:
    application.bot_data['client'] = ClientSession()
    logger.info('Клиент aiohttp запущен')


async def post_shutdown(application: Application) -> None:
    await application.bot_data['client'].close()
    logger.info('Клиент aiohttp остановлен')


if __name__ == '__main__':
    application = (
        Application.builder()
        .token(os.getenv('TELEGRAM_TOKEN', 'token'))
        .post_init(post_init)
        .rate_limiter(AIORateLimiter())
        .post_shutdown(post_shutdown)
        .build()
    )
    application.add_handler(CommandHandler('start', wake_up))
    application.add_handler(MessageHandler(
        filters.Regex('^Курс на сегодня$'), rates))
    application.run_polling()
