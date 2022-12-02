from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
# from telegram.ext import (
#     Dispatcher, CommandHandler,
#     MessageHandler, CallbackQueryHandler,
#     Filters,
#    # ConversationHandler,
# )
from tgbot.my_telegram import ConversationHandler

from dtb.constants import MessageTemplatesCode
from dtb.constants import StatusCode
from .messages import *
from .answers import *
from tgbot.handlers.main.messages import NO_ADMIN_GROUP
from tgbot.models import Status, User, UsertgGroups, tgGroups, UserReferrers, NewUser
from sheduler.models import MessageTemplates

from tgbot.handlers.utils import send_mess_by_tmplt
from tgbot.handlers.keyboard import make_keyboard
# from tgbot.handlers.main.answers import get_start_menu
# from tgbot.handlers.main.messages import get_start_mess
from tgbot import utils
# from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.utils import fill_file_id, send_photo


def end_registration(update:Update, context: CallbackContext, new_user: NewUser):
    user = User(user_id=new_user.user_id)
    user.username = new_user.username
    user.last_name = new_user.last_name
    user.first_name = new_user.first_name
    user.email = new_user.email
    user.telefon = new_user.telefon
    user.sur_name = new_user.sur_name
    user.date_of_birth = new_user.date_of_birth
    user.company = new_user.company
    user.job = new_user.job
    user.branch = new_user.branch
    user.citi = new_user.citi
    user.job_region = new_user.job_region
    user.site = new_user.site
    user.about = new_user.about
    user.created_at = new_user.created_at
    user.language_code = new_user.language_code
    user.deep_link = new_user.deep_link
    user.resident_urbanius_club = new_user.resident_urbanius_club
    user.business_club_member = new_user.business_club_member
    user.company_turnover = new_user.company_turnover
    user.number_of_employees = new_user.number_of_employees
    user.tags = new_user.tags
    user.main_photo = new_user.main_photo
    user.main_photo_id = new_user.main_photo_id
    user.status = Status.objects.get(code = StatusCode.APPLICANT)
    user.is_blocked_bot = True
    user.comment = "Ожидает подтверждения регистрации"
    user.save()
    new_user.update(registered=True)

    user.business_needs.set(new_user.business_needs.all())
    user.created_business_needs.set(new_user.created_business_needs.all())
    user.business_benefits.set(new_user.business_benefits.all())
    user.created_business_benefits.set(new_user.created_business_benefits.all())
    user.business_branches.set(new_user.business_branches.all())
    # Назначение пользователю рекомендателя, если он пришел по партнерской ссылке
    referrer = User.get_user_by_username_or_user_id(user.deep_link)
    if referrer:
        user_referer = UserReferrers(referrer = referrer, user = user)
        user_referer.save()
    # Назначение пользователю групп по умолчанию
    groups_set = tgGroups.objects.filter(for_all_users = True)
    for group in groups_set:
        user_group = UsertgGroups()
        user_group.group = group
        user_group.user = user
        user_group.save()
    if not user.main_photo_id:
        fill_file_id(user, "main_photo")
    # photo = user.main_photo.path
    photo_id = user.main_photo_id
    profile_txt = user.full_profile()

    send_photo(user.user_id, photo_id, caption=profile_txt)
    
    # reply_markup = make_keyboard_start_menu()
    # send_message(user_id = user.user_id, text = profile_txt, 
    #              disable_web_page_preview=True)

    reply_markup = make_keyboard(START,"usual",1)
    mess_template = MessageTemplates.objects.get(code=MessageTemplatesCode.WAIT_APPOVE_MESSAGE)
    send_mess_by_tmplt(user.user_id, mess_template, reply_markup) 


    group = tgGroups.get_group_by_name("Администраторы")
    if (group == None) or (group.chat_id == 0):
        update.message.reply_text(NO_ADMIN_GROUP)
    else:
        bn = {f"manage_new_user-{user.user_id}":"Посмотреть пользователя"}
        reply_markup =  make_keyboard(bn,"inline",1)
        text =f"Зарегистрирован новый пользователь @{utils.mystr(user.username)} {user.first_name} {utils.mystr(user.last_name)}"
        utils.send_message(group.chat_id, text, reply_markup =  reply_markup)
    context.user_data.clear()   
    return ConversationHandler.END