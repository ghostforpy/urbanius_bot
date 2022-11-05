from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters,
   # ConversationHandler,
)
from tgbot.my_telegram import ConversationHandler

from dtb.constants import MessageTemplatesCode
from dtb.constants import StatusCode
from .messages import *
from .answers import *
from tgbot.handlers.main.messages import NO_ADMIN_GROUP
from tgbot.models import Status, User, UsertgGroups, tgGroups, UserReferrers, NewUser
from sheduler.models import MessageTemplates

from tgbot.handlers.utils import send_message, send_mess_by_tmplt
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import get_start_mess
from tgbot import utils
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.utils import send_message


def prepare_ask_phone(update: Update, new_user: NewUser):
    update.message.reply_text(ASK_PHONE, reply_markup=make_keyboard(CANCEL,"usual",2,REQUEST_PHONE))

def prepare_ask_fio(update: Update, new_user: NewUser):
    fullname = " ".join([new_user.first_name, utils.mystr(new_user.last_name), utils.mystr(new_user.sur_name)])
    keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
    update.message.reply_text(ASK_FIO.format(fullname), reply_markup=keyboard)

def prepare_ask_about(update:Update, new_user: NewUser):
    # keyboard = make_keyboard(CANCEL,"usual",2)
    keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
    update.message.reply_text(ASK_ABOUT + f"\n Уже введено: '{utils.mystr(new_user.about)}'", reply_markup=keyboard)

def prepare_ask_birthday(update: Update, new_user: NewUser):
    # keyboard = make_keyboard(CANCEL,"usual",2)
    keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
    birthday = utils.mystr(new_user.date_of_birth)
    update.message.reply_text(ASK_BIRHDAY + f"\n Уже введено: '{birthday}'", reply_markup=keyboard)

def prepare_ask_email(update: Update, new_user: NewUser):
    # keyboard = make_keyboard(CANCEL,"usual",2)
    keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
    update.message.reply_text(ASK_EMAIL + f"\n Уже введено: '{utils.mystr(new_user.email)}'", reply_markup=keyboard)

def prepare_ask_citi(update: Update, new_user: NewUser):
    # keyboard = make_keyboard(CANCEL,"usual",2)
    keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
    update.message.reply_text(ASK_CITI + f"\n Уже введено: '{utils.mystr(new_user.citi)}'", reply_markup=keyboard)

def prepare_ask_company(update: Update, new_user: NewUser):
    # keyboard = make_keyboard(CANCEL,"usual",2)
    keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
    update.message.reply_text(ASK_COMPANY + f"\n Уже введено: '{utils.mystr(new_user.company)}'", reply_markup=keyboard)

def prepare_ask_job(update: Update, new_user: NewUser):
    # keyboard = make_keyboard(CANCEL,"usual",2)
    keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
    update.message.reply_text(ASK_JOB + f"\n Уже введено: '{utils.mystr(new_user.job)}'", reply_markup=keyboard)

def prepare_ask_site(update: Update, new_user: NewUser):
    # keyboard = make_keyboard(CANCEL,"usual",2)
    keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
    update.message.reply_text(ASK_SITE + f"\n Уже введено: '{utils.mystr(new_user.site)}'", reply_markup=keyboard)


