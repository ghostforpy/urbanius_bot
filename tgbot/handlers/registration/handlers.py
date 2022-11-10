import logging
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters,
   # ConversationHandler,
)
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from tgbot.models.business_benefits import BusinessBenefits
from tgbot.models.business_branches import BusinessBranches
from tgbot.models.business_needs import BusinessNeeds

from tgbot.my_telegram import ConversationHandler

from dtb.constants import StatusCode, MessageTemplatesCode
from .messages import *
from .answers import *
# from tgbot.handlers.main.messages import NO_ADMIN_GROUP
from sheduler.models import MessagesToSend
from tgbot.models import (
    Status,
    User,
    # UsertgGroups,
    # tgGroups,
    # UserReferrers,
    NewUser
)
from sheduler.models import MessageTemplates

# from tgbot.handlers.utils import send_message, send_mess_by_tmplt
from tgbot.handlers.files import _get_file_id

from tgbot.handlers.keyboard import make_keyboard
# from tgbot.handlers.main.answers import get_start_menu
# from tgbot.handlers.main.messages import get_start_mess
from tgbot import utils
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.utils import send_message
from .steps import STEPS
from .saveuser import end_registration
# from .utils import counter
from .prepares import prepare_create_business_needs, prepare_create_business_benefits


def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    context.user_data.clear()
    keyboard = make_keyboard(START,"usual",1)
    update.message.reply_text(REGISTRATION_CANCELED, reply_markup=keyboard)
    return ConversationHandler.END

def start_conversation(update: Update, context: CallbackContext):
    new_user, _ = NewUser.objects.get_or_create(user_id = update.message.from_user.id)
    # проверяем есть ли у пользователя в Телеграмм имя пользователя
    if new_user.username is None:
        update.message.reply_text(USERNAME_NEEDED)
        stop_conversation(update, context)
        return ConversationHandler.END
    update.message.reply_text(WELCOME_REG)
    # prepare_ask_first_name(update, new_user)
    f = STEPS["FIRSTNAME"]["self_prepare"]
    f(update, None)
    # update.message.reply_text(WELCOME_REG, reply_markup=make_keyboard(APPROVAL_ANSWERS,"usual",2))
    return STEPS["FIRSTNAME"]["step"]

def processing_firstname(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    # if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
    #    stop_conversation(update, context)
    #    return ConversationHandler.END
    # elif update.message.text == CANCEL_SKIP["skip"]:
    #     f = STEPS["FIRSTNAME"]["prepare"]
    #     f(update, new_user)
    #     # keyboard = make_keyboard(CANCEL,"usual",2)
    #     # update.message.reply_text(ASK_COMPANY + f"\n Уже введено: '{utils.mystr(new_user.company)}'", reply_markup=keyboard)
    #     return STEPS["FIRSTNAME"]["next"]
    # else: 
    new_user.first_name = update.message.text
    new_user.save()
    f = STEPS["FIRSTNAME"]["prepare"]
    f(update, new_user)
    # keyboard = make_keyboard(CANCEL,"usual",2)
    # update.message.reply_text(ASK_COMPANY + f"\n Уже введено: '{utils.mystr(new_user.company)}'", reply_markup=keyboard)
    return STEPS["FIRSTNAME"]["next"]

def processing_lastname(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    # if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
    #    stop_conversation(update, context)
    #    return ConversationHandler.END
    # elif update.message.text == CANCEL_SKIP["skip"]:
    #     f = STEPS["LASTNAME"]["prepare"]
    #     f(update, new_user)
    #     # keyboard = make_keyboard(CANCEL,"usual",2)
    #     # update.message.reply_text(ASK_COMPANY + f"\n Уже введено: '{utils.mystr(new_user.company)}'", reply_markup=keyboard)
    #     return STEPS["LASTNAME"]["next"]
    # else: 
    new_user.last_name = update.message.text
    new_user.save()
    f = STEPS["LASTNAME"]["prepare"]
    f(update, new_user)
    # keyboard = make_keyboard(CANCEL,"usual",2)
    # update.message.reply_text(ASK_COMPANY + f"\n Уже введено: '{utils.mystr(new_user.company)}'", reply_markup=keyboard)
    return STEPS["LASTNAME"]["next"]

def processing_surname(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    # if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
    #    stop_conversation(update, context)
    #    return ConversationHandler.END
    # elif update.message.text == CANCEL_SKIP["skip"]:
    #     f = STEPS["SURNAME"]["prepare"]
    #     f(update, new_user)
    #     # keyboard = make_keyboard(CANCEL,"usual",2)
    #     # update.message.reply_text(ASK_COMPANY + f"\n Уже введено: '{utils.mystr(new_user.company)}'", reply_markup=keyboard)
    #     return STEPS["SURNAME"]["next"]
    # else: 
    new_user.sur_name = update.message.text
    new_user.save()
    f = STEPS["SURNAME"]["prepare"]
    f(update, new_user)
    # keyboard = make_keyboard(CANCEL,"usual",2)
    # update.message.reply_text(ASK_COMPANY + f"\n Уже введено: '{utils.mystr(new_user.company)}'", reply_markup=keyboard)
    return STEPS["SURNAME"]["next"]


def processing_tags(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    new_user.tags = update.message.text
    new_user.save()
    f = STEPS["TAGS"]["prepare"]
    f(update, new_user)
    return STEPS["TAGS"]["next"]

def processing_aproval(update: Update, context: CallbackContext):
    if update.message.text not in [APPROVAL_ANSWERS[i] for i in APPROVAL_ANSWERS]:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(APPROVAL_ANSWERS,"usual",2))
    f = STEPS["APROVAL"]["prepare"]
    f(update, None)
    return STEPS["APROVAL"]["next"]
    # if update.message.text == APPROVAL_ANSWERS["yes"]: # В этом поле хранится согласие
    #     # update.message.reply_text(ASK_PHONE,  reply_markup=make_keyboard(CANCEL,"usual",2,REQUEST_PHONE))
    #     # prepare_ask_phone(update)
    #     f = STEPS["APROVAL"]["prepare"]
    #     # new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    #     f(update, None)
    #     return STEPS["APROVAL"]["next"]
    # elif update.message.text == APPROVAL_ANSWERS["no"]: # В этом поле хранится отказ
    #     stop_conversation(update, context)
    #     return ConversationHandler.END
    # else:
    #     update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(APPROVAL_ANSWERS,"usual",2))

def processing_resident_urbanius_club(update: Update, context: CallbackContext):
    # if update.message.text == CANCEL["cancel"]: # решили прервать регистрацию
    #    stop_conversation(update, context)
    #    return ConversationHandler.END
    if update.message.text not in [YES_NO[i] for i in YES_NO.keys()]:
        update.message.reply_text(
            ASK_REENTER + "\n" + ASK_RESIDENT_URBANIUS_CLUB,
            reply_markup=make_keyboard(YES_NO,"usual",2)
        )
        return
    new_user = None
    if update.message.text == YES_NO["yes"]:
        new_user = NewUser.objects.get(user_id = update.message.from_user.id)
        new_user.resident_urbanius_club = True
        new_user.save()
    f = STEPS["RESIDENT_URBANIUS_CLUB"]["prepare"]
    f(update, new_user)
    return STEPS["RESIDENT_URBANIUS_CLUB"]["next"]

def processing_business_club_member(update: Update, context: CallbackContext):
    new_user = None
    # if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
    #    stop_conversation(update, context)
    #    return ConversationHandler.END
    if update.message.text != NO["no"]:
        new_user = NewUser.objects.get(user_id = update.message.from_user.id)
        new_user.business_club_member = update.message.text
        new_user.save()
    f = STEPS["BUSINESS_CLUB_MEMBER"]["prepare"]
    f(update, new_user)
    return STEPS["BUSINESS_CLUB_MEMBER"]["next"]

def processing_company_turnover(update: Update, context: CallbackContext):
    if update.message is not None:
        update.message.reply_text(
            "Используйте предложенные варианты.",
            reply_markup=make_keyboard({},"usual",2)
        )
        f = STEPS["COMPANY_TURNOVER"]["self_prepare"]
        f(update, None)
        return
    query = update.callback_query
    variant = query.data
    query.answer()
    new_user = NewUser.objects.get(user_id = update.callback_query.from_user.id)
    new_user.company_turnover = variant
    new_user.save()
    f = STEPS["COMPANY_TURNOVER"]["prepare"]
    f(update, new_user)
    return STEPS["COMPANY_TURNOVER"]["next"]

def processing_company_number_of_employess(update: Update, context: CallbackContext):
    if update.message is not None:
        update.message.reply_text(
            "Используйте предложенные варианты.",
            reply_markup=make_keyboard({},"usual",2)
        )
        f = STEPS["COMPANY_NUMBER_OF_EMPLOYESS"]["self_prepare"]
        f(update, None)
        return
    query = update.callback_query
    variant = query.data
    query.answer()
    new_user = NewUser.objects.get(user_id = update.callback_query.from_user.id)
    new_user.number_of_employees = variant
    new_user.save()
    f = STEPS["COMPANY_NUMBER_OF_EMPLOYESS"]["prepare"]
    f(update, new_user)
    return STEPS["COMPANY_NUMBER_OF_EMPLOYESS"]["next"]

def processing_create_business_need(update: Update, context: CallbackContext):
    if update.message is not None:
        new_user = NewUser.objects.get(user_id = update.message.from_user.id)
        if update.message.text != CANCEL_CREATE["cancel"]:
            new_need = BusinessNeeds.objects.create(
                title=update.message.text[0].upper() + update.message.text[1:]
            )
            new_user.business_needs.add(new_need)
        f = STEPS["COMPANY_BUSINESS_NEEDS"]["self_prepare"]
        f(update, new_user)
        return STEPS["COMPANY_BUSINESS_NEEDS"]["step"]

def processing_company_business_needs(update: Update, context: CallbackContext):
    if update.message is not None:
        update.message.reply_text(
            "Используйте предложенные варианты.",
            reply_markup=make_keyboard({},"usual",2)
        )
        f = STEPS["COMPANY_BUSINESS_NEEDS"]["self_prepare"]
        new_user = NewUser.objects.get(user_id = update.message.from_user.id)
        f(update, new_user)
        return
    new_user = NewUser.objects.get(user_id = update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "create":
        prepare_create_business_needs(update)
        return "create_business_need"
    if variant == "next":
        f = STEPS["COMPANY_BUSINESS_NEEDS"]["prepare"]
        f(update, new_user)
        return STEPS["COMPANY_BUSINESS_NEEDS"]["next"]
    need = BusinessNeeds.objects.get(id=variant)
    if need in new_user.business_needs.all():
        new_user.business_needs.remove(need)
    else:
        new_user.business_needs.add(need)
    f = STEPS["COMPANY_BUSINESS_NEEDS"]["self_prepare"]
    f(update, new_user)
    return

def processing_company_business_branches(update: Update, context: CallbackContext):
    if update.message is not None:
        update.message.reply_text(
            "Используйте предложенные варианты.",
            reply_markup=make_keyboard({},"usual",2)
        )
        f = STEPS["COMPANY_BUSINESS_BRANCHES"]["self_prepare"]
        new_user = NewUser.objects.get(user_id = update.message.from_user.id)
        f(update, new_user)
        return
    new_user = NewUser.objects.get(user_id = update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "next":
        f = STEPS["COMPANY_BUSINESS_BRANCHES"]["prepare"]
        f(update, new_user)
        return STEPS["COMPANY_BUSINESS_BRANCHES"]["next"]
    branch = BusinessBranches.objects.get(id=variant)
    if branch in new_user.business_branches.all():
        new_user.business_branches.remove(branch)
        f = STEPS["COMPANY_BUSINESS_BRANCHES"]["self_prepare"]
        f(update, new_user)
        return
    else:
        if new_user.business_branches.count() < MAX_BUSINESS_BRANCHES:
            new_user.business_branches.add(branch)
        else:
            send_message(
                user_id=update.callback_query.from_user.id,
                text="Не допускается выбрать более {} вариантов".format(MAX_BUSINESS_BRANCHES),
                reply_markup=make_keyboard({},"inline",1)
            )
        f = STEPS["COMPANY_BUSINESS_BRANCHES"]["self_prepare"]
        f(update, new_user)
        return

def processing_create_business_benefit(update: Update, context: CallbackContext):
    if update.message is not None:
        new_user = NewUser.objects.get(user_id = update.message.from_user.id)
        if update.message.text != CANCEL_CREATE["cancel"]:
            new_need = BusinessBenefits.objects.create(
                title=update.message.text[0].upper() + update.message.text[1:]
            )
            new_user.business_benefits.add(new_need)
        f = STEPS["COMPANY_BUSINESS_BENEFITS"]["self_prepare"]
        f(update, new_user)
        return STEPS["COMPANY_BUSINESS_BENEFITS"]["step"]

def processing_company_business_benefits(update: Update, context: CallbackContext):
    if update.message is not None:
        update.message.reply_text(
            "Используйте предложенные варианты.",
            reply_markup=make_keyboard({},"usual",2)
        )
        f = STEPS["COMPANY_BUSINESS_BENEFITS"]["self_prepare"]
        new_user = NewUser.objects.get(user_id = update.message.from_user.id)
        f(update, new_user)
        return
    new_user = NewUser.objects.get(user_id = update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "create":
        prepare_create_business_benefits(update)
        return "create_business_benefit"
    if variant == "next":
        f = STEPS["COMPANY_BUSINESS_BENEFITS"]["prepare"]
        f(update, new_user)
        return STEPS["COMPANY_BUSINESS_BENEFITS"]["next"]
    benefit = BusinessBenefits.objects.get(id=variant)
    if benefit in new_user.business_benefits.all():
        new_user.business_benefits.remove(benefit)
    else:
        new_user.business_benefits.add(benefit)
    f = STEPS["COMPANY_BUSINESS_BENEFITS"]["self_prepare"]
    f(update, new_user)
    return

def processing_job_region(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    new_user.job_region = update.message.text
    new_user.save()
    f = STEPS["JOB_REGION"]["prepare"]
    f(update, new_user)
    return STEPS["JOB_REGION"]["next"]

def processing_deep_link(update: Update, context: CallbackContext):
    new_user = None
    # if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
    #    stop_conversation(update, context)
    #    return ConversationHandler.END
    if update.message.text != SKIP["skip"]:
        # проверяем наличие пользователя в базе
        if not User.get_user_by_username_or_user_id(update.message.text.replace("@","")):
            update.message.reply_text(
                ASK_DEEP_LINK_NO_USER,
                reply_markup=make_keyboard(SKIP,"usual",2)
            )
            return
        new_user = NewUser.objects.get(user_id = update.message.from_user.id)
        new_user.deep_link = update.message.text.replace("@","")

        new_user.save()
    f = STEPS["DEEP_LINK"]["prepare"]
    f(update, new_user)
    return STEPS["DEEP_LINK"]["next"]

def processing_company(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    # if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
    #    stop_conversation(update, context)
    #    return ConversationHandler.END
    # elif update.message.text == CANCEL_SKIP["skip"]:
    #     f = STEPS["COMPANY"]["prepare"]
    #     f(update, new_user)
    #     # keyboard = make_keyboard(CANCEL,"usual",2)
    #     # update.message.reply_text(ASK_JOB + f"\n Уже введено: '{utils.mystr(new_user.job)}'", reply_markup=keyboard)
    #     return STEPS["COMPANY"]["next"]
    # else: 
    new_user.company = update.message.text
    new_user.save()
    f = STEPS["COMPANY"]["prepare"]
    f(update, new_user)
    # keyboard = make_keyboard(CANCEL,"usual",2)
    # update.message.reply_text(ASK_JOB + f"\n Уже введено: '{utils.mystr(new_user.job)}'", reply_markup=keyboard)
    return STEPS["COMPANY"]["next"]

def processing_citi(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    # if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
    #    stop_conversation(update, context)
    #    return ConversationHandler.END
    # elif update.message.text == CANCEL_SKIP["skip"]:
    #     f = STEPS["CITI"]["prepare"]
    #     f(update, new_user)
    #     # keyboard = make_keyboard(CANCEL,"usual",2)
    #     # update.message.reply_text(ASK_COMPANY + f"\n Уже введено: '{utils.mystr(new_user.company)}'", reply_markup=keyboard)
    #     return STEPS["CITI"]["next"]
    # else: 
    new_user.citi = update.message.text
    new_user.save()
    f = STEPS["CITI"]["prepare"]
    f(update, new_user)
    # keyboard = make_keyboard(CANCEL,"usual",2)
    # update.message.reply_text(ASK_COMPANY + f"\n Уже введено: '{utils.mystr(new_user.company)}'", reply_markup=keyboard)
    return STEPS["CITI"]["next"]

def processing_job(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    # if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
    #    stop_conversation(update, context)
    #    return ConversationHandler.END
    # elif update.message.text == CANCEL_SKIP["skip"]:
    #     f = STEPS["JOB"]["prepare"]
    #     f(update, new_user)
    #     # keyboard = make_keyboard(CANCEL,"usual",2)
    #     # update.message.reply_text(ASK_SITE + f"\n Уже введено: '{utils.mystr(new_user.site)}'", reply_markup=keyboard)
    #     return STEPS["JOB"]["next"]
    # else: 
    new_user.job = update.message.text
    new_user.save()
    f = STEPS["JOB"]["prepare"]
    f(update, new_user)
    # keyboard = make_keyboard(CANCEL,"usual",2)
    # update.message.reply_text(ASK_SITE + f"\n Уже введено: '{utils.mystr(new_user.site)}'", reply_markup=keyboard)
    return STEPS["JOB"]["next"]

def processing_fio(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    if update.message.text == CANCEL["cancel"]:
        stop_conversation(update, context)
        return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        f = STEPS["FIO"]["prepare"]
        f(update, new_user)
        # keyboard = make_keyboard(CANCEL,"usual",2)
        # update.message.reply_text(ASK_ABOUT + f"\n Уже введено: '{utils.mystr(utils.mystr(new_user.about))}'", reply_markup=keyboard)
        return STEPS["FIO"]["next"]
    else:
        fio = update.message.text.split()
        len_fio = len(fio)
        if len_fio == 1:
            new_user.first_name = fio[0] # Имя
        elif len_fio == 2:
            new_user.first_name = fio[0] # Имя
            new_user.last_name = fio[1]  # Фамилия
        elif len_fio > 2:
            new_user.last_name = fio[0]  # Фамилия
            new_user.first_name = fio[1] # Имя
            new_user.sur_name = fio[2]   # Отчество
        new_user.save()
        f = STEPS["FIO"]["prepare"]
        f(update, new_user)
        # keyboard = make_keyboard(CANCEL,"usual",2)
        # update.message.reply_text(ASK_ABOUT + f"\n Уже введено: '{utils.mystr(new_user.about)}'", reply_markup=keyboard)
        return STEPS["FIO"]["next"]

def processing_birhday(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    date = utils.is_date(update.message.text)
    if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
       stop_conversation(update, context)
       return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        f = STEPS["BIRTHDAY"]["prepare"]
        f(update, new_user)
        # keyboard = make_keyboard(CANCEL,"usual",2)
        # update.message.reply_text(ASK_EMAIL + f"\n Уже введено: '{utils.mystr(new_user.email)}'", reply_markup=keyboard)
        return STEPS["BIRTHDAY"]["next"]
    elif not(date): # ввели неверную дату
        update.message.reply_text(BAD_DATE, reply_markup=make_keyboard(CANCEL,"usual",2))
        return
    else: # ввели верный дату
        new_user.date_of_birth = date
        new_user.save()
        f = STEPS["BIRTHDAY"]["prepare"]
        f(update, new_user)
        # keyboard = make_keyboard(CANCEL,"usual",2)
        # update.message.reply_text(ASK_EMAIL + f"\n Уже введено: '{utils.mystr(new_user.email)}'", reply_markup=keyboard)
        return STEPS["BIRTHDAY"]["next"]

def processing_about(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    if update.message.text == CANCEL["cancel"]:
        stop_conversation(update, context)
        return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        f = STEPS["ABOUT"]["prepare"]
        f(update, new_user)
        # prepare_ask_birthday(update, new_user.date_of_birth)
        # keyboard = make_keyboard(CANCEL,"usual",2)
        # update.message.reply_text(ASK_BIRHDAY + f"\n Уже введено: '{utils.mystr(new_user.date_of_birth)}'", reply_markup=keyboard)
        return STEPS["ABOUT"]["next"]
    else:
        new_user.about = update.message.text 
        new_user.save()
        f = STEPS["ABOUT"]["prepare"]
        f(update, new_user)
        # prepare_ask_birthday(update, new_user.date_of_birth)
        # keyboard = make_keyboard(CANCEL,"usual",2)
        # birthday = utils.mystr(new_user.date_of_birth)
        # update.message.reply_text(ASK_BIRHDAY + f"\n Уже введено: '{birthday}'", reply_markup=keyboard)
        return STEPS["ABOUT"]["next"]

def processing_site(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    # if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
    #    stop_conversation(update, context)
    #    return ConversationHandler.END
    # # elif update.message.text == CANCEL_SKIP["skip"]:
    # #     site = ""
    # else:
    validate = URLValidator()
    site = update.message.text
    try:
        validate(site)
    except ValidationError:
        update.message.reply_text(BAD_SITE, reply_markup=make_keyboard({},"usual",2))
        return
    new_user.site = site
    new_user.registered = True
    new_user.save()
    f = STEPS["SITE"]["prepare"]
    f(update, new_user)
    return STEPS["SITE"]["next"]
    # return end_registration(update, context, new_user)

def processing_phone(update: Update, context: CallbackContext):
    if update.message.contact != None: # Был прислан контакт        
        # Запоминаем телефон
        new_user = NewUser.objects.get(user_id = update.message.from_user.id)
        new_user.telefon = update.message.contact.phone_number
        new_user.save()
        if isinstance(STEPS["PHONE"]["next"], int):
            f = STEPS["PHONE"]["prepare"]
            f(update, new_user)
            return STEPS["PHONE"]["next"]
        else:
            return end_registration(update, context, new_user)
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard({},"usual",2,REQUEST_PHONE))

def processing_photo(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    # if update.message.photo != None:
    # user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    foto_id, filename_orig = _get_file_id(update.message)
    filename_lst = filename_orig.split(".")
    newFile = context.bot.get_file(foto_id)
    filename = utils.get_uniq_file_name(settings.BASE_DIR / "media/user_fotos",filename_lst[0],filename_lst[1])
    newFile.download(settings.BASE_DIR / ("media/user_fotos/"+filename))
    new_user.main_photo = "user_fotos/"+filename
    new_user.main_photo_id = foto_id
    new_user.save()
    if isinstance(STEPS["PHOTO"]["next"], int):
        f = STEPS["PHOTO"]["prepare"]
        f(update, new_user)
        return STEPS["PHOTO"]["next"]
    else:
        return end_registration(update, context, new_user)
    # else:
    #     update.message.reply_text(
    #         "Пришлите именно фотографию",
    #         reply_markup=make_keyboard({},"usual",2,{})
    #     )

def processing_photo_txt(update: Update, context: CallbackContext):
    update.message.reply_text("Пришлите именно фотографию")
    return
# def processing_about_fin(update: Update, context: CallbackContext):
#     new_user = NewUser.objects.get(user_id = update.message.from_user.id)
#     if update.message.text == CANCEL["cancel"]:
#         stop_conversation(update, context)
#         return ConversationHandler.END
#     elif update.message.text == CANCEL_SKIP["skip"]:
#         about = ""   
#     else:
#         about = update.message.text 

#     new_user.about = about
#     new_user.registered = True
#     new_user.save()

#     user = User(user_id=new_user.user_id)
#     user.username = new_user.username
#     user.last_name = new_user.last_name
#     user.first_name = new_user.first_name
#     user.email = new_user.email
#     user.telefon = new_user.telefon
#     user.sur_name = new_user.sur_name
#     user.date_of_birth = new_user.date_of_birth
#     user.company = new_user.company
#     user.job = new_user.job
#     user.branch = new_user.branch
#     user.citi = new_user.citi
#     user.job_region = new_user.job_region
#     user.site = new_user.site
#     user.about = new_user.about
#     user.created_at = new_user.created_at
#     user.language_code = new_user.language_code
#     user.deep_link = new_user.deep_link
#     user.status = Status.objects.get(code = StatusCode.APPLICANT)
#     user.is_blocked_bot = True
#     user.comment = "Ожидает подтверждения регистрации"
#     user.save()
#     # Назначение пользователю рекомендателя, если он пришел по партнерской ссылке
#     referrer = User.get_user_by_username_or_user_id(user.deep_link)
#     if referrer:
#         user_referer = UserReferrers(referrer = referrer, user = user)
#         user_referer.save()
#     # Назначение пользователю групп по умолчанию
#     groups_set = tgGroups.objects.filter(for_all_users = True)
#     for group in groups_set:
#         user_group = UsertgGroups()
#         user_group.group = group
#         user_group.user = user
#         user_group.save()
        
#     reply_markup = make_keyboard(START,"usual",1)
#     mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.WELCOME_NEWUSER_MESSAGE)

#     send_mess_by_tmplt(user.user_id, mess_template, reply_markup) 

#     group = tgGroups.get_group_by_name("Администраторы")
#     if (group == None) or (group.chat_id == 0):
#         update.message.reply_text(NO_ADMIN_GROUP)
#     else:
#         bn = {f"manage_new_user-{user.user_id}":"Посмотреть пользователя"}
#         reply_markup =  make_keyboard(bn,"inline",1)
#         text =f"Зарегистрирован новый пользователь @{utils.mystr(user.username)} {user.first_name} {utils.mystr(user.last_name)}"
#         send_message(group.chat_id, text, reply_markup =  reply_markup)
#     context.user_data.clear()   
#     return ConversationHandler.END



# #--------------------------------------------------
# #-------Дальше не идем. Пользователи тупые-------------





# def processing_email(update: Update, context: CallbackContext):
#     new_user = NewUser.objects.get(user_id = update.message.from_user.id)
#     email = utils.is_email(update.message.text)

#     if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
#        stop_conversation(update, context)
#        return ConversationHandler.END
#     elif update.message.text == CANCEL_SKIP["skip"]:
#         prepare_ask_citi(update, new_user.citi)
#         # keyboard = make_keyboard(CANCEL,"usual",2)
#         # update.message.reply_text(ASK_CITI + f"\n Уже введено: '{utils.mystr(new_user.citi)}'", reply_markup=keyboard)
#         return EMAIL + 1
#     elif not(email): # ввели неверную email
#         update.message.reply_text(BAD_EMAIL,reply_markup=make_keyboard(CANCEL,"usual",2))
#         return    
#     else: 
#         new_user.email = email
#         new_user.save()
#         prepare_ask_citi(update, new_user.citi)
#         # keyboard = make_keyboard(CANCEL,"usual",2)
#         # update.message.reply_text(ASK_CITI + f"\n Уже введено: '{utils.mystr(new_user.citi)}'", reply_markup=keyboard)
#         return EMAIL + 1

#-----------------------------------------------------------------------------
#----------------Manage new user----------------------------------------------

def stop_conversation_new_user(update: Update, context: CallbackContext):
    """ 
       Возврат к главному меню    
    """
    # Заканчиваем разговор.
    if update.message:
        user_id = update.message.from_user.id
    else:
        query = update.callback_query
        query.answer()
        user_id = query.from_user.id
        # query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
        # query.edit_message_text("Подтверждение завершено", reply_markup=make_keyboard(EMPTY,"inline",1))
        query.delete_message()

    # user = User.get_user_by_username_or_user_id(user_id)
    # send_message(user_id=user_id, text=FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
    # send_message(user_id=user_id, text=get_start_mess(user), reply_markup=get_start_menu(user))
    # return ConversationHandler.END

def manage_new_user(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    if (not user) or (not user.is_admin):
        text ="Нет прав администратора"
        send_message(update.callback_query.message.chat_id, text)
        return
    query_data = query.data.split("-")
    new_user_id = int(query_data[1])
    new_user = User.get_user_by_username_or_user_id(new_user_id)
    profile_text = new_user.full_profile()
    manage_usr_btn = {f"confirm_reg-{new_user_id}":"Подтвердить регистрацию",
                      f"uncofirm_reg-{new_user_id}":"Отклонить регистрацию",
                      f"back_from_user_confirm-{new_user_id}":"Отмена обработки",
                     }
    reply_markup=make_keyboard(manage_usr_btn,"inline",1)
    send_message(user_id = user_id, text=profile_text, reply_markup=reply_markup)

    bn = {f"manage_new_user-{new_user.user_id}":"Посмотреть пользователя"}
    reply_markup =  make_keyboard(bn,"inline",1)       
    text = query.message.text.split('\n')[0]
    text += f'\nПрофиль пользователя отправлен в чат {context.bot.name} '
    text += f'пользователю {query.from_user.full_name}'
    query.edit_message_text(text=text, reply_markup=reply_markup)

    return "wait_new_user_comand"

def confirm_registration(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)
    query_data = query.data.split("-")
    new_user_id = int(query_data[1])
    new_user = User.get_user_by_username_or_user_id(new_user_id)
    new_user.is_blocked_bot = False
    new_user.status =  Status.objects.get(code = StatusCode.GROUP_MEMBER)
    new_user.comment = "Регистрация подтверждена"
    new_user.save()
    text = MessageTemplates.objects.get(code=MessageTemplatesCode.WAIT_APPOVE_MESSAGE)
    # text = "Ваша регистрация подтверждена. Наберите /start для обновления меню."
    send_message(new_user_id, text.text)
    # query.edit_message_text("Подтверждение завершено", reply_markup=make_keyboard(EMPTY,"inline",1))
    query.delete_message()
    # query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
    # send_message(user_id=user_id, text=FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
    # send_message(user_id=user_id, text=get_start_mess(user), reply_markup=get_start_menu(user))
    # return ConversationHandler.END

def setup_dispatcher_conv(dp: Dispatcher):
    conv_handler_reg = ConversationHandler( # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[MessageHandler(Filters.text(REGISTRATION_START_BTN["reg_start"]) & FilterPrivateNoCommand, start_conversation)],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            STEPS["FIRSTNAME"]["step"]:[MessageHandler(Filters.text & FilterPrivateNoCommand, processing_firstname)],
            STEPS["LASTNAME"]["step"]:[MessageHandler(Filters.text & FilterPrivateNoCommand, processing_lastname)],
            STEPS["SURNAME"]["step"]:[MessageHandler(Filters.text & FilterPrivateNoCommand, processing_surname)],
            STEPS["CITI"]["step"]: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_citi)],
            STEPS["COMPANY"]["step"]: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_company)],
            STEPS["JOB"]["step"]: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_job)],
            STEPS["SITE"]["step"]: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_site)],
            STEPS["JOB_REGION"]["step"]: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_job_region)],
            STEPS["COMPANY_TURNOVER"]["step"]: [
                CallbackQueryHandler(processing_company_turnover),
                MessageHandler(Filters.text & FilterPrivateNoCommand, processing_company_turnover)
                ],
            STEPS["COMPANY_NUMBER_OF_EMPLOYESS"]["step"]: [
                CallbackQueryHandler(processing_company_number_of_employess),
                MessageHandler(Filters.text & FilterPrivateNoCommand, processing_company_number_of_employess)
                ],
            STEPS["COMPANY_BUSINESS_NEEDS"]["step"]: [
                CallbackQueryHandler(processing_company_business_needs),
                MessageHandler(Filters.text & FilterPrivateNoCommand, processing_company_business_needs)
                ],
            "create_business_need": [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_create_business_need)],
            STEPS["TAGS"]["step"]: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_tags)],

            STEPS["COMPANY_BUSINESS_BENEFITS"]["step"]: [
                CallbackQueryHandler(processing_company_business_benefits),
                MessageHandler(Filters.text & FilterPrivateNoCommand, processing_company_business_benefits)
                ],
            "create_business_benefit": [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_create_business_benefit)],
            STEPS["COMPANY_BUSINESS_BRANCHES"]["step"]: [
                CallbackQueryHandler(processing_company_business_branches),
                MessageHandler(Filters.text & FilterPrivateNoCommand, processing_company_business_branches)
                ],
            STEPS["RESIDENT_URBANIUS_CLUB"]["step"]: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_resident_urbanius_club)],
            STEPS["BUSINESS_CLUB_MEMBER"]["step"]: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_business_club_member)],
            STEPS["DEEP_LINK"]["step"]: [MessageHandler(Filters.text & FilterPrivateNoCommand, processing_deep_link)],
            STEPS["APROVAL"]["step"]:[MessageHandler(Filters.text & FilterPrivateNoCommand, processing_aproval)],
            STEPS["PHONE"]["step"]: [MessageHandler((Filters.contact | Filters.text) & FilterPrivateNoCommand, processing_phone)],
            STEPS["PHOTO"]["step"]:[
                MessageHandler(Filters.photo & FilterPrivateNoCommand, processing_photo),
                MessageHandler(Filters.text & FilterPrivateNoCommand, processing_photo_txt)
                ],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private)]
    )
    dp.add_handler(conv_handler_reg)

    dp.add_handler(CallbackQueryHandler(manage_new_user, pattern="^manage_new_user-"))
    dp.add_handler(CallbackQueryHandler(stop_conversation_new_user, pattern="^back_from_user_confirm-"))
    dp.add_handler(CallbackQueryHandler(confirm_registration, pattern="^confirm_reg-"))
    dp.add_handler(CallbackQueryHandler(stop_conversation_new_user, pattern="^uncofirm_reg-"))
     
    # conv_handler_confirm_reg = ConversationHandler( 
    #     # точка входа в разговор
    #     entry_points=[CallbackQueryHandler(manage_new_user, pattern="^manage_new_user-")],
    #     states={
    #         "wait_new_user_comand":[                                  
    #                    CallbackQueryHandler(stop_conversation_new_user, pattern="^back$"),
    #                    CallbackQueryHandler(confirm_registration, pattern="^confirm_reg-"),
    #                    CallbackQueryHandler(stop_conversation_new_user, pattern="^uncofirm_reg-"),
    #                   ],
    #     },
    #     # точка выхода из разговора
    #     fallbacks=[CommandHandler('cancel', stop_conversation_new_user, Filters.chat_type.private),
    #                CommandHandler('start', stop_conversation_new_user, Filters.chat_type.private)]
    # )
    # dp.add_handler(conv_handler_confirm_reg)
