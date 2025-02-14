from telegram.update import Update
from telegram import ReplyKeyboardRemove
from telegram.ext.callbackcontext import CallbackContext
# from telegram.ext import (
#     Dispatcher, CommandHandler,
#     MessageHandler, CallbackQueryHandler,
#     Filters,
#    # ConversationHandler,
# )
# from tgbot.models.business_benefits import BusinessBenefits
# from tgbot.my_telegram import ConversationHandler

# from dtb.constants import MessageTemplatesCode
# from dtb.constants import StatusCode
from .messages import *
from .answers import *
# from tgbot.handlers.main.messages import NO_ADMIN_GROUP
from tgbot.models import (
    # Status, User, UsertgGroups,
    # tgGroups, UserReferrers, 
    NewUser, AbstractTgUser, BusinessNeeds, BusinessBranches, BusinessBenefits
)
# from sheduler.models import MessageTemplates

# from tgbot.handlers.utils import send_message, send_mess_by_tmplt
from tgbot.handlers.keyboard import make_keyboard
# from tgbot.handlers.main.answers import get_start_menu
# from tgbot.handlers.main.messages import get_start_mess
from tgbot import utils
# from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.utils import send_message


def prepare_approval(update: Update, context: CallbackContext, new_user: NewUser):
    kwargs = {
        "text": ASK_APPROVAL,
        "reply_markup": make_keyboard(APPROVAL_ANSWERS,"usual",2)
    }
    if update.message is not None:
        update.message.reply_text(
            **kwargs
        )
    elif update.callback_query:
        send_message(
            user_id=update.callback_query.from_user.id,
            **kwargs
        )
    elif update.chosen_inline_result:
        send_message(
            user_id=update.chosen_inline_result.from_user.id,
            **kwargs
        )

def prepare_resident_urbanius_club(update: Update, context: CallbackContext, new_user: NewUser):
    if update.message is not None:
        update.message.reply_text(
            ASK_RESIDENT_URBANIUS_CLUB,
            reply_markup=make_keyboard(YES_NO,"usual",2)
        )
    elif update.callback_query is not None:
        send_message(
            user_id=update.callback_query.from_user.id,
            text=ASK_RESIDENT_URBANIUS_CLUB,
            reply_markup=make_keyboard(YES_NO,"usual",2)
        )

def prepare_business_club_member(update: Update, context: CallbackContext, new_user: NewUser):
    update.message.reply_text(
        ASK_BUSINESS_CLUB_MEMBER,
        reply_markup=make_keyboard(NO,"usual",2)
    )

def prepare_job_region(update: Update, context: CallbackContext, new_user: NewUser):
    update.message.reply_text(
        ASK_JOB_REGION,
        reply_markup=make_keyboard({},"usual",2)
    )

def prepare_tags(update: Update, context: CallbackContext, new_user: NewUser):
    if update.message is not None:
        update.message.reply_text(
            ASK_TAGS,
            reply_markup=ReplyKeyboardRemove()
        )
    elif update.callback_query is not None:
        send_message(
            user_id=update.callback_query.from_user.id,
            text=ASK_TAGS,
            reply_markup=ReplyKeyboardRemove()
        )

def prepare_deep_link(update: Update, context: CallbackContext, new_user: NewUser):
    update.message.reply_text(
        ASK_DEEP_LINK,
        reply_markup=make_keyboard(FIND_MEMB,"inline",1)
    )

def prepare_company_turnover(update: Update, context: CallbackContext, new_user: NewUser):
    company_turnovers = {
        item[0]: item[1] for item in AbstractTgUser.COMPANY_TURNOVERS_CHOISES
    }
    update.message.reply_text(
        ASK_COMPANY_TURNOVER,
        reply_markup=make_keyboard(company_turnovers,"inline",1)
    )

def prepare_company_number_of_employees(update: Update, context: CallbackContext, new_user: NewUser):
    company_number_of_employees = {
        item[0]: item[1] for item in AbstractTgUser.COMPANY_NUMBER_OF_EMPLOYESS_CHOISES
    }
    if update.message is not None:
        update.message.reply_text(
            ASK_COMPANY_NUMBER_OF_EMPLOYESS,
            reply_markup=make_keyboard(company_number_of_employees,"inline",1)
        )
    elif update.callback_query is not None:
        update.callback_query.edit_message_text(
            ASK_COMPANY_NUMBER_OF_EMPLOYESS,
            reply_markup=make_keyboard(
                company_number_of_employees,
                "inline",
                1,
            )
        )

def prepare_create_business_needs(update:Update):
    kwargs = {
        "text": ASK_CREATE_COMPANY_BUSINESS_NEEDS,
        "reply_markup": make_keyboard(
                CANCEL_CREATE,
                "inline",
                1,
            )
    }
    if update.message is not None:
        update.message.reply_text(**kwargs)
    elif update.callback_query is not None:
        update.callback_query.edit_message_text(**kwargs)

def prepare_company_business_needs(update: Update, context: CallbackContext, new_user: NewUser):
    company_business_needs = dict()
    for n in BusinessNeeds.get_needs_by_user(new_user):
    # for n in BusinessNeeds.objects.all():
        company_business_needs[str(n.id)] = n.title
        if n in new_user.business_needs.all():
            company_business_needs[str(n.id)] = CHECK_ICON + company_business_needs[str(n.id)]
    footer_buttons = CREATE.copy()
    if new_user.business_needs.count() > 0:
        footer_buttons.update(NEXT)
    kwargs = {
        "text": ASK_COMPANY_BUSINESS_NEEDS,
        "reply_markup": make_keyboard(
                company_business_needs,
                "inline",
                1,
                footer_buttons=footer_buttons
            )
    }
    if update.message is not None:
        update.message.reply_text(**kwargs)
    elif update.callback_query is not None:
        update.callback_query.edit_message_text(**kwargs)

def prepare_company_business_benefits(update: Update, context: CallbackContext, new_user: NewUser):
    company_business_benefits = dict()
    # for n in BusinessBenefits.objects.all():
    for n in BusinessBenefits.get_benefits_by_user(new_user):
        company_business_benefits[str(n.id)] = n.title
        if n in new_user.business_benefits.all():
            company_business_benefits[str(n.id)] = CHECK_ICON + company_business_benefits[str(n.id)]
    footer_buttons = CREATE.copy()
    if new_user.business_benefits.count() > 0:
        footer_buttons.update(NEXT)
    kwargs = {
        "text": ASK_COMPANY_COMPANY_BUSINESS_BENEFITS,
        "reply_markup": make_keyboard(
                company_business_benefits,
                "inline",
                1,
                footer_buttons=footer_buttons
            )
    }
    if update.message is not None:
        update.message.reply_text(**kwargs)
    elif update.callback_query is not None:
        update.callback_query.edit_message_text(**kwargs)

def prepare_create_business_benefits(update:Update):
    kwargs = {
        "text": ASK_CREATE_COMPANY_BUSINESS_BENEFITS,
        "reply_markup": make_keyboard(
                CANCEL_CREATE,
                "inline",
                1,
            )
    }
    if update.message is not None:
        update.message.reply_text(**kwargs)
    elif update.callback_query is not None:
        update.callback_query.edit_message_text(**kwargs)

def prepare_company_business_branches(update: Update, context: CallbackContext, new_user: NewUser):
    company_business_branches = dict()
    for n in BusinessBranches.objects.all():
        company_business_branches[str(n.id)] = n.title
        if n in new_user.business_branches.all():
            company_business_branches[str(n.id)] = CHECK_ICON + company_business_branches[str(n.id)]
    footer_buttons = NEXT if new_user.business_branches.count() > 0 else []
    if update.message is not None:
        update.message.reply_text(
            ASK_COMPANY_COMPANY_BUSINESS_BRANCHES,
            reply_markup=make_keyboard(
                company_business_branches,
                "inline",
                1,
                footer_buttons=footer_buttons
            )
        )
    elif update.callback_query is not None:
        update.callback_query.edit_message_text(
            ASK_COMPANY_COMPANY_BUSINESS_BRANCHES,
            reply_markup=make_keyboard(
                company_business_branches,
                "inline",
                1,
                footer_buttons=footer_buttons
            )
        )

def prepare_ask_phone(update: Update, context: CallbackContext, new_user: NewUser):
    update.message.reply_text(ASK_PHONE, reply_markup=make_keyboard({},"usual",2,REQUEST_PHONE))

def prepare_ask_photo(update: Update, context: CallbackContext, new_user: NewUser):
    if context.user_data.get("bad_phone_registration", False):
        send_message(
            user_id=update.message.from_user.id,
            text=ASK_PHOTO,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        update.message.reply_text(ASK_PHOTO, reply_markup=ReplyKeyboardRemove())

def prepare_ask_fio(update: Update, context: CallbackContext, new_user: NewUser):
    fullname = " ".join([new_user.first_name, utils.mystr(new_user.last_name), utils.mystr(new_user.sur_name)])
    keyboard = make_keyboard(CANCEL_SKIP,"usual",2)
    update.message.reply_text(ASK_FIO.format(fullname), reply_markup=keyboard)

def prepare_ask_first_name(update: Update, context: CallbackContext, new_user: NewUser):
    # fullname = " ".join([new_user.first_name, utils.mystr(new_user.last_name), utils.mystr(new_user.sur_name)])
    keyboard = make_keyboard({},"usual",2)
    update.message.reply_text(ASK_FIRSTNAME, reply_markup=keyboard)

def prepare_ask_surname(update: Update, context: CallbackContext, new_user: NewUser):
    # fullname = " ".join([new_user.first_name, utils.mystr(new_user.last_name), utils.mystr(new_user.sur_name)])
    keyboard = make_keyboard({},"usual",2)
    update.message.reply_text(ASK_SURNAME, reply_markup=keyboard)

def prepare_ask_lastname(update: Update, context: CallbackContext, new_user: NewUser):
    # fullname = " ".join([new_user.first_name, utils.mystr(new_user.last_name), utils.mystr(new_user.sur_name)])
    keyboard = make_keyboard({},"usual",2)
    update.message.reply_text(ASK_LASTNAME, reply_markup=keyboard)

def prepare_ask_about(update: Update, context: CallbackContext, new_user: NewUser):
    keyboard = make_keyboard(CANCEL,"usual",2)
    update.message.reply_text(ASK_ABOUT + f"\n Уже введено: '{utils.mystr(new_user.about)}'", reply_markup=keyboard)

def prepare_ask_birthday(update: Update, context: CallbackContext, new_user: NewUser):
    keyboard = make_keyboard(CANCEL,"usual",2)
    birthday = utils.mystr(new_user.date_of_birth)
    update.message.reply_text(ASK_BIRHDAY + f"\n Уже введено: '{birthday}'", reply_markup=keyboard)

def prepare_ask_email(update: Update, context: CallbackContext, new_user: NewUser):
    keyboard = make_keyboard(CANCEL,"usual",2)
    update.message.reply_text(ASK_EMAIL + f"\n Уже введено: '{utils.mystr(new_user.email)}'", reply_markup=keyboard)

def prepare_ask_citi(update: Update, context: CallbackContext, new_user: NewUser):
    keyboard = make_keyboard({},"usual",2)
    update.message.reply_text(ASK_CITI, reply_markup=keyboard)
    # update.message.reply_text(ASK_CITI + f"\n Уже введено: '{utils.mystr(new_user.citi)}'", reply_markup=keyboard)

def prepare_ask_company(update: Update, context: CallbackContext, new_user: NewUser):
    keyboard = make_keyboard({},"usual",2)
    update.message.reply_text(ASK_COMPANY, reply_markup=keyboard)
    # update.message.reply_text(ASK_COMPANY + f"\n Уже введено: '{utils.mystr(new_user.company)}'", reply_markup=keyboard)

def prepare_ask_job(update: Update, context: CallbackContext, new_user: NewUser):
    keyboard = make_keyboard({},"usual",2)
    update.message.reply_text(ASK_JOB, reply_markup=keyboard)
    # update.message.reply_text(ASK_JOB + f"\n Уже введено: '{utils.mystr(new_user.job)}'", reply_markup=keyboard)

def prepare_ask_site(update: Update, context: CallbackContext, new_user: NewUser):
    keyboard = make_keyboard({},"usual",2)
    # update.message.reply_text(ASK_SITE + f"\n Уже введено: '{utils.mystr(new_user.site)}'", reply_markup=keyboard)
    update.message.reply_text(ASK_SITE, reply_markup=keyboard)


