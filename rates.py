import asyncio
import logging
import os
from datetime import datetime

from aiohttp import ClientError, ClientSession, ClientTimeout
from telegram import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import (AIORateLimiter, Application, CommandHandler,
                          MessageHandler, filters)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

URL_TEMPLATE = ('https://openexchangerates.org/api/latest.json'
                + f'?app_id={os.getenv("API_TOKEN")}'
                + '&symbols=RUB%2CEUR%2CAMD%2CCNY')
RATES_MESSAGE = ('Курсы валют на {date} UTC 💸\n\n'
                 + 'Евро 🇪🇺 -> Доллар 🇺🇸: {eur_usd}\n\n'
                 + 'Доллар 🇺🇸 -> Рубль 🇷🇺: {usd_rub}\n'
                 + 'Евро 🇪🇺 -> Рубль 🇷🇺: {eur_rub}\n\n'
                 + 'Доллар 🇺🇸 -> Юань 🇨🇳: {usd_cny}\n'
                 + 'Юань 🇨🇳 -> Рубль 🇷🇺: {cny_rub}\n\n'
                 + 'Драм 🇦🇲 -> Рубль 🇷🇺: {amd_rub}\n'
                 + 'Рубль 🇷🇺 -> Драм 🇦🇲: {rub_amd}\n'
                 + 'Доллар 🇺🇸 -> Драм 🇦🇲: {usd_amd}\n'
                 + 'Евро 🇪🇺 -> Драм 🇦🇲: {eur_amd}'
                 )

DEFAULT_KEYBOARD = ReplyKeyboardMarkup(
    [['Курс на сегодня']],
    resize_keyboard=True,
    one_time_keyboard=False,
    is_persistent=True,
)


def build_keyboard(web_app_url):
    buttons = [[KeyboardButton('Курс на сегодня')]]
    if web_app_url:
        buttons[0].append(
            KeyboardButton('Конвертер', web_app=WebAppInfo(url=web_app_url))
        )
    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )


def get_keyboard(context):
    return context.bot_data.get('keyboard', DEFAULT_KEYBOARD)


async def rates(update, context):
    chat = update.effective_chat
    logger.info(f'User {chat.id} requested rates')
    try:
        client = context.bot_data['client']
        async with client.get(url=URL_TEMPLATE) as response:
            response.raise_for_status()
            data = await response.json()
        timestamp_value = data.get('timestamp')
        rates = data.get('rates')
        if timestamp_value is None or rates is None:
            raise ValueError('Missing rates data')
    except (ClientError, asyncio.TimeoutError, ValueError) as exc:
        logger.warning('Failed to fetch currency rates', exc_info=exc)
        await context.bot.send_message(
            chat_id=chat.id,
            text='Не удалось получить курс. Попробуйте позже.',
            reply_markup=get_keyboard(context),
        )
        return
    timestamp = datetime.fromtimestamp(timestamp_value)
    rates_text = RATES_MESSAGE.format(
        date=timestamp,
        eur_usd=f"{round(1/rates['EUR'], 3):.3f}",
        usd_rub=f"{round(rates['RUB'], 2):.2f}",
        eur_rub=f"{round(rates['RUB']/rates['EUR'], 2):.2f}",
        usd_cny=f"{round(rates['CNY'], 3):.3f}",
        cny_rub=f"{round(rates['RUB']/rates['CNY'], 4):.4f}",
        amd_rub=f"{round(rates['AMD']/rates['RUB'], 3):.3f}",
        rub_amd=f"{round(rates['RUB']/rates['AMD'], 4):.4f}",
        usd_amd=f"{round(rates['AMD'], 2):.2f}",
        eur_amd=f"{round(rates['AMD']/rates['EUR'], 2):.2f}",
    )
    await context.bot.send_message(
        chat_id=chat.id,
        text=rates_text,
        reply_markup=get_keyboard(context),
    )


async def on_all(update, context):
    chat = update.effective_chat
    await context.bot.send_message(
        chat_id=chat.id,
        text=('Неизвестная команда'),
        reply_markup=get_keyboard(context),
    )
    logger.info(f'User {chat.id} entered an unknown command')


async def wake_up(update, context):
    chat = update.effective_chat
    await context.bot.send_message(
        chat_id=chat.id,
        text=('Привет!'),
        reply_markup=get_keyboard(context),
    )
    logger.info(f'User {chat.id} started the bot')


async def post_init(application: Application) -> None:
    web_app_url = os.getenv('MINI_APP_URL')
    application.bot_data['keyboard'] = build_keyboard(web_app_url)
    application.bot_data['client'] = ClientSession(
        timeout=ClientTimeout(total=10),
    )
    if not web_app_url:
        logger.warning('MINI_APP_URL is not set; mini app button disabled')
    logger.info('aiohttp client started')


async def post_shutdown(application: Application) -> None:
    await application.bot_data['client'].close()
    logger.info('aiohttp client stopped')


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
    application.add_handler(MessageHandler(filters.ALL, on_all))
    application.run_polling()
