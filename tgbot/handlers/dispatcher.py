# -*- coding: utf-8 -*-

"""Telegram event handlers."""
import pytz
import telegram

from telegram.ext import (
    Updater, Dispatcher, Filters,
    CommandHandler, MessageHandler, 
    InlineQueryHandler, CallbackQueryHandler,
    ChosenInlineResultHandler, PollAnswerHandler, Defaults
)


from dtb.settings import TELEGRAM_TOKEN

from tgbot.handlers import commands
from tgbot.handlers.registration.handlers import setup_dispatcher_reg
from tgbot.handlers.main.handlers import setup_dispatcher_main
from tgbot.handlers.profile.handlers import setup_dispatcher_prof

def setup_dispatcher(dp: Dispatcher):
    """
    Adding handlers for events from Telegram
    """

    dp.add_handler(CommandHandler("start", commands.command_start, Filters.chat_type.private))

    setup_dispatcher_reg(dp) #заполнение обработчиков регистрации
    setup_dispatcher_main(dp) #заполнение обработчиков главного диалога
    setup_dispatcher_prof(dp) #заполнение обработчиков работы с профайлом

    dp.add_handler(MessageHandler(Filters.text & Filters.chat_type.private, commands.command_start))
    # EXAMPLES FOR HANDLERS
    # dp.add_handler(MessageHandler(Filters.text, <function_handler>))
    # dp.add_handler(MessageHandler(
    #     Filters.document, <function_handler>,
    # ))
    # dp.add_handler(CallbackQueryHandler(<function_handler>, pattern="^r\d+_\d+"))
    # dp.add_handler(MessageHandler(
    #     Filters.chat(chat_id=int(TELEGRAM_FILESTORAGE_ID)),
    #     # & Filters.forwarded & (Filters.photo | Filters.video | Filters.animation),
    #     <function_handler>,
    # ))

    return dp


def run_pooling():

    defaults = Defaults(parse_mode=telegram.ParseMode.HTML, tzinfo=pytz.timezone('Europe/Moscow'))
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True, defaults=defaults)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = telegram.Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f"https://t.me/" + bot_info["username"]

    print(f"Pooling of '{bot_link}' started")
    updater.start_polling(timeout=123, drop_pending_updates=True)
    updater.idle()


def process_telegram_event(update_json):
    update = telegram.Update.de_json(update_json, bot)
    dispatcher.process_update(update)


# Global variable - best way I found to init Telegram bot
bot = telegram.Bot(TELEGRAM_TOKEN)
dispatcher = setup_dispatcher(Dispatcher(bot, None, workers=0, use_context=True))
TELEGRAM_BOT_USERNAME = bot.get_me()["username"]