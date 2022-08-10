import os
import urllib.parse as urllibparse
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters,
    ConversationHandler,
)
from telegram import InputMediaDocument, MessageEntity

from django.conf import settings
from .messages import *
from .answers import *
from tgbot.handlers.main.answers import START_MENU_FULL
import tgbot.models as mymodels
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start
from tgbot.handlers.utils import send_message
from tgbot.utils import extract_user_data_from_update, mystr, is_date, is_email, get_uniq_file_name
from tgbot.handlers.files import _get_file_id
from tgbot.handlers.registration.messages import REGISTRATION_START_MESSS
# Возврат к главному меню в исключительных ситуациях
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    update.message.reply_text(PROF_FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
    command_start(update, context)
    return ConversationHandler.END

# Временная заглушка
def blank(update: Update, context: CallbackContext):
    pass

def bad_callback_enter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(EMPTY,"usual",2))

# Начало работы с профилем
def start_conversation(update: Update, context: CallbackContext):
    query = update.callback_query
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query.answer()
    query.edit_message_text(text=REGISTRATION_START_MESSS)
    send_message(user_id=user.user_id, text=PROF_HELLO, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))

    return "working"

# Обработчик фамилиии
def manage_fio(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    fio = " ".join([mystr(user.last_name), mystr(user.first_name), mystr(user.sur_name)])
    update.message.reply_text(ASK_FIO.format(fio), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_fio"
  
def manage_fio_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        fio = update.message.text.split()
        len_fio = len(fio)
        if len_fio == 1:
            user.last_name = ""  # Фамилия
            user.first_name = fio[0] # Имя
            user.sur_name = ""   # Отчество
        elif len_fio == 2:
            user.first_name = fio[0] # Имя
            user.last_name = fio[1]  # Фамилия
            user.sur_name = ""   # Отчество
        elif len_fio > 2:
            user.last_name = fio[0]  # Фамилия
            user.first_name = fio[1] # Имя
            user.sur_name = fio[2]   # Отчество
        user.save()
        text = "ФИО изменены"
    else:
        text = "ФИО не изменены"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"
#-------------------------------------------  
# Обработчик телефона
def manage_phone(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_PHONE.format(user.telefon), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_phone"

def manage_phone_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.telefon = update.message.text
        user.save()
        text = "Телефон изменен"
    else:
        text = "Телефон не изменен"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"
#-------------------------------------------  
# Обработчик о себе
def manage_about(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_ABOUT.format(user.about), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_about"

def manage_about_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.about = update.message.text
        user.save()
        text = "Информация 'О себе' изменена"
    else:
        text = "Информация 'О себе' не изменена"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"
#-------------------------------------------  
# Обработчик Город
def manage_citi(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_CITI.format(user.citi), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_citi"

def manage_citi_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.citi = update.message.text
        user.save()
        text = "Город изменен"
    else:
        text = "Город не изменен"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"
#-------------------------------------------  
# Обработчик Компания
def manage_company(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_COMPANY.format(user.company), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_company"

def manage_company_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.company = update.message.text
        user.save()
        text = "Компания изменена"
    else:
        text = "Компания не изменена"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"

#-------------------------------------------  
# Обработчик Должность
def manage_job(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_JOB.format(user.job), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_job"

def manage_job_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.job = update.message.text
        user.save()
        text = "Должность изменена"
    else:
        text = "Должность не изменена"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"

#-------------------------------------------  
# Обработчик Сайт
def manage_site(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_SITE.format(user.site), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_site"

def manage_site_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.site = update.message.text
        user.save()
        text = "Сайт изменен"
    else:
        text = "Сайт не изменен"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"

#-------------------------------------------  
# Обработчик День рождения
def manage_date_of_birth(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_BIRHDAY.format(user.date_of_birth), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_date_of_birth"

def manage_date_of_birth_action(update: Update, context: CallbackContext):
    date = is_date(update.message.text)
    text = ""
    if update.message.text == SKIP["skip"]:        
        text = "День рождения не изменен"
    elif not(date): # ввели неверную дату
        update.message.reply_text(BAD_DATE, make_keyboard(SKIP,"usual",1))
        return 
    else:
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.date_of_birth = date
        user.save()
        text = "День рождения изменен"
        
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"
#-------------------------------------------  
# Обработчик e-mail
def manage_email(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_EMAIL.format(user.email), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_email"

def manage_email_action(update: Update, context: CallbackContext):
    email = is_email(update.message.text)
    text = ""
    if update.message.text == SKIP["skip"]:        
        text = "e-mail не изменен"
    elif not(email): # ввели неверную email
        update.message.reply_text(BAD_EMAIL, make_keyboard(SKIP,"usual",1))
        return 
    else:
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.email = email
        user.save()
        text = "e-mail изменен"
        
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"
#-------------------------------------------  
# Обработчик Теги
def manage_tags(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_TAGS.format(user.tags), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_tags"

def manage_tags_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.tags = update.message.text
        user.save()
        text = "Теги изменены"
    else:
        text = "Теги  не изменены"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"

#-------------------------------------------  
# Обработчик Фото
def manage_main_photo(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    if not(user.main_photo):
        photo = settings.BASE_DIR / 'media/no_foto.jpg'
    else:
        photo = user.main_photo.path
    if os.path.exists(photo):
        update.message.reply_photo(open(photo, 'rb'), caption = ASK_FOTO, reply_markup=make_keyboard(SKIP,"usual",1))
    else:
        update.message.reply_text(NOT_FOTO.format(user.tags), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_main_photo"

def manage_main_photo_action(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    foto_id, filename_orig = _get_file_id(update.message)
    filename_lst = filename_orig.split(".")
    newFile = context.bot.get_file(foto_id)
    filename = get_uniq_file_name(settings.BASE_DIR / "media/user_fotos",filename_lst[0],filename_lst[1])
    newFile.download(settings.BASE_DIR / ("media/user_fotos/"+filename))
    user.main_photo = "user_fotos/"+filename
    user.save()
    text = "Фото изменено"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"

def manage_main_photo_txt_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text == SKIP["skip"]:        
        text = "Фото  не изменено"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    else:
        text = "Пришлите именно фотографию или пропустите шаг"
        update.message.reply_text(text,reply_markup=make_keyboard(SKIP,"usual",1))
        return "choose_action_main_photo"
#-------------------------------------------  
# Обработчик Региона
def manage_job_region(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_REGION.format(user.job_region), reply_markup=make_keyboard(CHANGE_SKIP,"usual",2))
    return "choose_action_job_region"

def manage_job_region_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text == CHANGE_SKIP["skip"]:        
        text = "Регион  не изменен"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    elif update.message.text == CHANGE_SKIP["change"]:
        update.message.reply_text("Редактирование региона", reply_markup=make_keyboard(EMPTY,"usual",1))
        all_regions = mymodels.get_dict(mymodels.JobRegions,"pk","code")
        all_regions_txt = mymodels.get_model_text(mymodels.JobRegions,["code","name"])
        text = "Выберите номер региона\n"+all_regions_txt
        update.message.reply_text(text, reply_markup=make_keyboard(all_regions,"inline",8))
        return "select_region"
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(CHANGE_SKIP,"usual",2))

def process_region(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    new_reg = mymodels.JobRegions.objects.get(pk=int(variant))

    # редактируем сообщение, тем самым кнопки 
    # в чате заменятся на этот ответ.

    query.edit_message_text(text=f"Выбранный вариант: {str(new_reg)}")
    user.job_region = new_reg
    user.save()
    text = "Регион  изменен"
    reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
    send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
    return "working"

#-------------------------------------------  
# Обработчик Отрасли
def manage_branch(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_BRANCH.format(user.branch), reply_markup=make_keyboard(CHANGE_SKIP,"usual",2))
    return "choose_action_branch"

def manage_branch_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text == CHANGE_SKIP["skip"]:        
        text = "Отрасль  не изменена"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    elif update.message.text == CHANGE_SKIP["change"]:
        update.message.reply_text("Редактирование отрасли", reply_markup=make_keyboard(EMPTY,"usual",1))
        all_branchs = mymodels.get_dict(mymodels.Branch,"pk","NN")
        all_branchs_txt = mymodels.get_model_text(mymodels.Branch,["NN","name"])
        text = "Выберите номер отрасли\n"+all_branchs_txt
        update.message.reply_text(text, reply_markup=make_keyboard(all_branchs,"inline",8))
        return "select_branch"
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(CHANGE_SKIP,"usual",2))

def process_branch(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    new_reg = mymodels.Branch.objects.get(pk=int(variant))

    # редактируем сообщение, тем самым кнопки 
    # в чате заменятся на этот ответ.

    query.edit_message_text(text=f"Выбранный вариант: {str(new_reg)}")
    user.branch = new_reg
    user.save()
    text = "Отрасль  изменена"
    reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
    send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
    return "working"

#-------------------------------------------  
# Обработчик Статус
def manage_status(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(SAY_STATUS.format(user.status), reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"

#-------------------------------------------  
# Обработчик Группы
def manage_groups(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    all_groups = mymodels.get_model_text(mymodels.UsertgGroups,["NN","group"], user)
    update.message.reply_text(SAY_GROUPS.format(str(all_groups)), reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"

#-------------------------------------------  
# Обработчик потребности
def manage_needs(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_NEEDS.format(user.needs), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_needs"

def manage_needs_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.needs = update.message.text
        user.save()
        text = "Потребности изменены"
    else:
        text = "Потребности не изменены"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"
        
#-------------------------------------------  
# Обработчик Спорта
def manage_sport(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    all_sport = mymodels.get_model_text(mymodels.UserSport,["NN","sport"], user)
    update.message.reply_text(ASK_SPORT.format(str(all_sport)), reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))
    return "choose_action_sport"

def manage_sport_action(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)    
    if update.message.text == ADD_DEL_SKIP["skip"]:        
        text = "Виды спорта не изменены"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    elif update.message.text == ADD_DEL_SKIP["del"]:
        update.message.reply_text("Удаление видов спорта", reply_markup=make_keyboard(EMPTY,"usual",1))
        all_sport = mymodels.get_dict(mymodels.UserSport,"pk","sport", user)
        #all_sport_txt = mymodels.get_model_text(mymodels.UserSport,["NN","sport"], user)
        text = "Выберите удаляемый вид спорта"
        update.message.reply_text(text, reply_markup=make_keyboard(all_sport,"inline",2,None,FINISH))
        return "delete_sport"
    elif update.message.text == ADD_DEL_SKIP["add"]:
        all_user_sport_txt = mymodels.get_model_text(mymodels.UserSport,["NN","sport"], user)
        all_sport_txt = mymodels.get_model_text(mymodels.Sport,["NN","name"])
        all_sport = mymodels.get_dict(mymodels.Sport,"pk","NN")
        update.message.reply_text("Добавление видов спорта", reply_markup=make_keyboard(EMPTY,"usual",1))
        text = "Возможные виды спорта:\n"
        text += all_sport_txt
        text += "\nВаши виды спорта:\n"
        text += all_user_sport_txt
        text += "Введите номер добавляемого вида спорта"
        update.message.reply_text(text, reply_markup=make_keyboard(all_sport,"inline",8,None,FINISH))
        return "add_sport"
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))

def delete_sport(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "finish":
        all_sport_txt = mymodels.get_model_text(mymodels.UserSport,["NN","sport"], user)
        query.edit_message_text(text=all_sport_txt)
        text = "Удаление видов спорта завершено"
        reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "working"
    else:
        sport = mymodels.UserSport.objects.get(pk=int(variant))
        sport.delete()
        all_sport = mymodels.get_dict(mymodels.UserSport,"pk","sport", user)
        if len(all_sport) == 0:
            all_sport_txt = "Все виды спорта удалены"
            query.edit_message_text(text=all_sport_txt)
            text = "Удаление видов спорта завершено"
            reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
            send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
            return "working"
        else:           
            #all_sport_txt = mymodels.get_model_text(mymodels.UserSport,["NN","sport"], user)
            text = "Выберите удаляемый вид спорта"
            query.edit_message_text(text, reply_markup=make_keyboard(all_sport,"inline",2,None,FINISH))

def add_sport(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "finish":
        all_sport_txt = mymodels.get_model_text(mymodels.UserSport,["NN","sport"], user)
        query.edit_message_text(text=all_sport_txt)
        text = "Добавление видов спорта  завершено"
        reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "working"
    else:
        sport = mymodels.Sport.objects.get(pk=int(variant))
        user_sports = mymodels.UserSport.objects.filter(sport = sport, user = user)
        if len(user_sports) == 0:
            user_sport = mymodels.UserSport(sport = sport, user = user)
            user_sport.save()
            all_user_sport_txt = mymodels.get_model_text(mymodels.UserSport,["NN","sport"], user)
            all_sport_txt = mymodels.get_model_text(mymodels.Sport,["NN","name"])
            all_sport = mymodels.get_dict(mymodels.Sport,"pk","NN")
            text = "Возможные виды спорта :\n"
            text += all_sport_txt
            text += "\nВаши виды спорта :\n"
            text += all_user_sport_txt
            text += "Введите номер добавляемго вида спорта "
            query.edit_message_text(text, reply_markup=make_keyboard(all_sport,"inline",8,None,FINISH))
        
#-------------------------------------------  
# Обработчик Хобби
def manage_hobby(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    all_hobby = mymodels.get_model_text(mymodels.UserHobby,["NN","hobby"], user)
    update.message.reply_text(ASK_HOBBY.format(str(all_hobby)), reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))
    return "choose_action_hobby"

def manage_hobby_action(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)    
    if update.message.text == ADD_DEL_SKIP["skip"]:        
        text = "Виды хобби не изменены"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    elif update.message.text == ADD_DEL_SKIP["del"]:
        update.message.reply_text("Удаление видов хобби", reply_markup=make_keyboard(EMPTY,"usual",1))
        all_hobby = mymodels.get_dict(mymodels.UserHobby,"pk","hobby", user)
        #all_hobby_txt = mymodels.get_model_text(mymodels.UserHobby,["NN","hobby"], user)
        text = "Выберите удаляемый вид хобби"
        update.message.reply_text(text, reply_markup=make_keyboard(all_hobby,"inline",2,None,FINISH))
        return "delete_hobby"
    elif update.message.text == ADD_DEL_SKIP["add"]:
        all_user_hobby_txt = mymodels.get_model_text(mymodels.UserHobby,["NN","hobby"], user)
        all_hobby_txt = mymodels.get_model_text(mymodels.Hobby,["NN","name"])
        all_hobby = mymodels.get_dict(mymodels.Hobby,"pk","NN")
        update.message.reply_text("Добавление видов хобби", reply_markup=make_keyboard(EMPTY,"usual",1))
        text = "Возможные виды хобби:\n"
        text += all_hobby_txt
        text += "\nВаши виды хобби:\n"
        text += all_user_hobby_txt
        text += "Введите номер добавляемого вида хобби"
        update.message.reply_text(text, reply_markup=make_keyboard(all_hobby,"inline",8,None,FINISH))
        return "add_hobby"
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))

def delete_hobby(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "finish":
        all_hobby_txt = mymodels.get_model_text(mymodels.UserHobby,["NN","hobby"], user)
        query.edit_message_text(text=all_hobby_txt)
        text = "Удаление видов хобби завершено"
        reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "working"
    else:
        hobby = mymodels.UserHobby.objects.get(pk=int(variant))
        hobby.delete()
        all_hobby = mymodels.get_dict(mymodels.UserHobby,"pk","hobby", user)
        if len(all_hobby) == 0:
            all_hobby_txt = "Все виды хобби удалены"
            query.edit_message_text(text=all_hobby_txt)
            text = "Удаление видов хобби завершено"
            reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
            send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
            return "working"
        else:           
            #all_hobby_txt = mymodels.get_model_text(mymodels.UserHobby,["NN","hobby"], user)
            text ="Выберите удаляемый вид хобби"
            query.edit_message_text(text, reply_markup=make_keyboard(all_hobby,"inline",2,None,FINISH))

def add_hobby(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "finish":
        all_hobby_txt = mymodels.get_model_text(mymodels.UserHobby,["NN","hobby"], user)
        query.edit_message_text(text=all_hobby_txt)
        text = "Добавление видов хобби  завершено"
        reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "working"
    else:
        hobby = mymodels.Hobby.objects.get(pk=int(variant))
        user_hobbys = mymodels.UserHobby.objects.filter(hobby = hobby, user = user)
        if len(user_hobbys) == 0:
            user_hobby = mymodels.UserHobby(hobby = hobby, user = user)
            user_hobby.save()
            all_user_hobby_txt = mymodels.get_model_text(mymodels.UserHobby,["NN","hobby"], user)
            all_hobby_txt = mymodels.get_model_text(mymodels.Hobby,["NN","name"])
            all_hobby = mymodels.get_dict(mymodels.Hobby,"pk","NN")
            text = "Возможные виды хобби :\n"
            text += all_hobby_txt
            text += "\nВаши виды хобби :\n"
            text += all_user_hobby_txt
            text += "Введите номер добавляемго вида хобби "
            query.edit_message_text(text, reply_markup=make_keyboard(all_hobby,"inline",8,None,FINISH))
        
#-------------------------------------------  
# Обработчик Предложений
def manage_offers(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    offers_set = user.offers_set.all()
    if len(offers_set) == 0:
        update.message.reply_text(NO_OFFERS, reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))
    else:
        media_group = []
        for offer in offers_set:
            if not(offer.image):
                file = settings.BASE_DIR / 'media/no_file'
            else:               
                if os.path.exists( offer.image.path): # если файл пропал, чтоб ошибки не было
                    file = offer.image.path
                else:
                    file = settings.BASE_DIR / 'media/no_file'
            media_group.append(InputMediaDocument(open(file, 'rb'), caption=offer.offer))
        update.message.reply_text(ASK_OFFERS, reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))
        update.message.reply_media_group(media_group)
    
    return "choose_action_offers"

def manage_offers_action(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)    
    if update.message.text == ADD_DEL_SKIP["skip"]:        
        text = "Ваши предложения не изменены"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    elif update.message.text == ADD_DEL_SKIP["del"]:
        update.message.reply_text("Удаление предложений", reply_markup=make_keyboard(EMPTY,"usual",1))
        all_offers = mymodels.get_dict(mymodels.Offers,"pk","offer", user)
        #all_offers_txt = mymodels.get_model_text(mymodels.Offers,["NN","offer","image"], user)
        text = "Выберите удаляемое предложение"
        update.message.reply_text(text, reply_markup=make_keyboard(all_offers,"inline",1,None,FINISH))
        return "delete_offers"
    elif update.message.text == ADD_DEL_SKIP["add"]:
        all_offers_txt = mymodels.get_model_text(mymodels.Offers,["NN","offer","image"], user)
        text = ADD_OFFERS+"\nВаши предложения \n" + all_offers_txt        
        update.message.reply_text(text, reply_markup=make_keyboard(FINISH,"usual",1))
        return "add_offers"
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))

def delete_offers(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "finish":
        all_offers_txt = mymodels.get_model_text(mymodels.Offers,["NN","offer","image"], user)
        query.edit_message_text(text=all_offers_txt)
        text = "Удаление предложений завершено"
        reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "working"
    else:
        offers = mymodels.Offers.objects.get(pk=int(variant))
        offers.delete()
        all_offers = mymodels.get_dict(mymodels.Offers,"pk","offer", user)
        if len(all_offers) == 0:
            all_offers_txt = "Все предложения удалены"
            query.edit_message_text(text=all_offers_txt)
            text = "Удаление предложений завершено"
            reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
            send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
            return "working"
        else:           
            #all_offers_txt = mymodels.get_model_text(mymodels.Offers,["NN","offer","image"], user)
            text = text = "Выберите удаляемое предложение"
            query.edit_message_text(text, reply_markup=make_keyboard(all_offers,"inline",1,None,FINISH))

def add_offers(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    if update.message.text == FINISH["finish"]:        
        text = "Завершено добавление предложений"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    if update.message.text != None:
        text = update.message.text
    elif update.message.caption != None:
        text = update.message.caption
    else:
        text = ""
    
    doc_id, filename_orig = _get_file_id(update.message)
    if doc_id != None:
        filename_lst = filename_orig.split(".")
        newFile = context.bot.get_file(doc_id)
        filename = get_uniq_file_name(settings.BASE_DIR / "media/offers",filename_lst[0],filename_lst[1])
        newFile.download(settings.BASE_DIR / ("media/offers/"+filename))
        image = "offers/"+filename
    else:
        image = None
    offer = mymodels.Offers()
    offer.image = image
    offer.offer = text
    offer.user = user
    offer.save()   
    all_offers_txt = mymodels.get_model_text(mymodels.Offers,["NN","offer","image"], user)
    text = ADD_OFFERS+"\nВаши предложения \n" + all_offers_txt
    update.message.reply_text(text, reply_markup=make_keyboard(FINISH,"usual",1))

#-------------------------------------------  
# Обработчик Соцсетей
def manage_social_nets(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    all_social_nets_txt = mymodels.get_model_text(mymodels.SocialNets,["NN","soc_net_site", "link"], user)
    update.message.reply_text(ASK_SOC_NET.format(str(all_social_nets_txt)), reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2), disable_web_page_preview=True)
    return "choose_action_social_nets"

def manage_social_nets_action(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)    
    if update.message.text == ADD_DEL_SKIP["skip"]:        
        text = "Соцсети не изменены"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    elif update.message.text == ADD_DEL_SKIP["del"]:
        update.message.reply_text("Удаление соцсетей", reply_markup=make_keyboard(EMPTY,"usual",1))
        all_social_nets = mymodels.get_dict(mymodels.SocialNets,"pk","soc_net_site", user)
        text = "Выберите удаляемую соцсеть"
        update.message.reply_text(text, reply_markup=make_keyboard(all_social_nets,"inline",2,None,FINISH))
        return "delete_social_nets"
    elif update.message.text == ADD_DEL_SKIP["add"]:
        all_social_nets_txt = mymodels.get_model_text(mymodels.SocialNets,["NN","soc_net_site", "link"], user)
        text = all_social_nets_txt + "\nДля добавления соц. сети введите ссылку на вашу страницу"
        update.message.reply_text(text, reply_markup=make_keyboard(FINISH,"usual",1), disable_web_page_preview=True)

        return "add_social_nets"
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))

def delete_social_nets(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "finish":
        all_social_nets_txt = mymodels.get_model_text(mymodels.SocialNets,["NN","soc_net_site"], user)
        query.edit_message_text(text=all_social_nets_txt)
        text = "Удаление соцсетей завершено"
        reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "working"
    else:
        social_nets = mymodels.SocialNets.objects.get(pk=int(variant))
        social_nets.delete()
        all_social_nets = mymodels.get_dict(mymodels.SocialNets,"pk","soc_net_site", user)
        if len(all_social_nets) == 0:
            all_social_nets_txt = "Все соцсети удалены"
            query.edit_message_text(text=all_social_nets_txt)
            text = "Удаление соцсетей завершено"
            reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
            send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
            return "working"
        else:           
            text ="Выберите удаляемую соцсеть"
            query.edit_message_text(text, reply_markup=make_keyboard(all_social_nets,"inline",2,None,FINISH))

def add_social_nets(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    if update.message.text == FINISH["finish"]:        
        text = "Завершено добавление соц. сетей"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    elif (len(update.message.entities)>0)and(update.message.entities[0].type == "url"):
        url = update.message.text
        parsed_url = urllibparse.urlparse(url)
        site_name = parsed_url.hostname
        url_parts = list(parsed_url)
        url_parts[2] = ""
        url_parts[3] = ""
        url_parts[4] = ""
        url_parts[5] = ""
        site_url = urllibparse.urlunparse(url_parts)
        user_soc_net_set = user.socialnets_set.filter(link = url)
        if len(user_soc_net_set) == 0:
            soc_net_site_set = mymodels.SocialNetSites.objects.filter(link = site_url)
            if len(soc_net_site_set) == 0:
                soc_net_site = mymodels.SocialNetSites(name = site_name, link = site_url)
                soc_net_site.save()
            else:
                soc_net_site = soc_net_site_set[0]
            user_soc_net = mymodels.SocialNets(soc_net_site = soc_net_site, link = url, user = user)
            user_soc_net.save()
        
        all_social_nets_txt = mymodels.get_model_text(mymodels.SocialNets,["NN","soc_net_site", "link"], user)
        text = all_social_nets_txt + "\nДля добавления соц. сети введите ссылку на вашу страницу"
        update.message.reply_text(text, reply_markup=make_keyboard(FINISH,"usual",1), disable_web_page_preview=True)

    else:
        text = "Введите именно ссылку на web страницу"
        update.message.reply_text(text, reply_markup=make_keyboard(FINISH,"usual",1), disable_web_page_preview=True)

#-------------------------------------------  
# Обработчик Рекомендатели
def manage_referes(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    all_referes_txt = mymodels.get_model_text(mymodels.UserReferrers,["NN","referrer"], user)
    update.message.reply_text(ASK_REFERES.format(str(all_referes_txt)), reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2), disable_web_page_preview=True)
    return "choose_action_referes"

def manage_referes_action(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)    
    if update.message.text == ADD_DEL_SKIP["skip"]:        
        text = "Рекомендатели не изменены"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    elif update.message.text == ADD_DEL_SKIP["del"]:
        update.message.reply_text("Удаление рекомендателей", reply_markup=make_keyboard(EMPTY,"usual",1))
        all_referes = mymodels.get_dict(mymodels.UserReferrers,"pk","referrer", user)
        text = "Выберите удаляемого рекомендателя"
        update.message.reply_text(text, reply_markup=make_keyboard(all_referes,"inline",2,None,FINISH))
        return "delete_referes"
    elif update.message.text == ADD_DEL_SKIP["add"]:
        all_referes_txt = mymodels.get_model_text(mymodels.UserReferrers,["NN","referrer"], user)
        text = all_referes_txt + "\nДля добавления рекомендателя введите его фамилию"
        update.message.reply_text(text, reply_markup=make_keyboard(FINISH,"usual",1))

        return "add_referes"
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))


def delete_referes(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "finish":
        all_referes_txt = mymodels.get_model_text(mymodels.UserReferrers,["NN","referrer"], user)
        query.edit_message_text(text=all_referes_txt)
        text = "Удаление рекомендателей завершено"
        reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "working"
    else:
        referer = mymodels.UserReferrers.objects.get(pk=int(variant))
        referer.delete()
        all_referes = mymodels.get_dict(mymodels.UserReferrers,"pk","referrer", user)
        if len(all_referes) == 0:
            all_referes_txt = "Все рекомендатели удалены"
            query.edit_message_text(text=all_referes_txt)
            text = "Удаление рекомендателей завершено"
            reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
            send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
            return "working"
        else:           
            text ="Выберите удаляемого рекомендателя"
            query.edit_message_text(text, reply_markup=make_keyboard(all_referes,"inline",2,None,FINISH))

def add_referes(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    if update.message.text == FINISH["finish"]:        
        text = "Завершено добавление рекомендателей"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    else:
        selected_users = mymodels.get_dict(mymodels.User,"pk","first_name,last_name", None,{"last_name":update.message.text})
        if len(selected_users) == 0:
            text = "Такие пользователи не найдены. Повторите ввод или завершите добавление"        
            update.message.reply_text(text, reply_markup=make_keyboard(FINISH,"usual",1), disable_web_page_preview=True)
            return "add_referes"
        else:
            update.message.reply_text("Выбор рекомендателя", reply_markup=make_keyboard(EMPTY,"usual",1))
            text = "Выберите рекомендателя"
            update.message.reply_text(text, reply_markup=make_keyboard(selected_users,"inline",1,None,FINISH))
            return "select_referes"

def select_referes(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "finish":
        all_referes_txt = mymodels.get_model_text(mymodels.UserReferrers,["NN","referrer"], user)
        query.edit_message_text(text=all_referes_txt)
        text = "Добавление рекомендателей завершено"
        reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "working"
    else:
        referer = mymodels.User.objects.get(pk=int(variant))
        user_referers =mymodels.UserReferrers.objects.filter(referrer = referer, user = user)
        if len(user_referers) == 0:
            user_referer = mymodels.UserReferrers(referrer = referer, user = user)
            user_referer.save()  
        all_referes_txt = mymodels.get_model_text(mymodels.UserReferrers,["NN","referrer"], user)
        query.edit_message_text(text=all_referes_txt)
        text = "Для добавления рекомендателя введите его фамилию"
        reply_markup=make_keyboard(FINISH,"usual",1)
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "add_referes"


def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^profile$", run_async=True)],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[
                       MessageHandler(Filters.text([PROF_MENU["fio"]]) & FilterPrivateNoCommand, manage_fio, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["telefon"]]) & FilterPrivateNoCommand, manage_phone, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["about"]]) & FilterPrivateNoCommand, manage_about, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["citi"]]) & FilterPrivateNoCommand, manage_citi, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["company"]]) & FilterPrivateNoCommand, manage_company, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["job"]]) & FilterPrivateNoCommand, manage_job, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["site"]]) & FilterPrivateNoCommand, manage_site, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["date_of_birth"]]) & FilterPrivateNoCommand, manage_date_of_birth, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["email"]]) & FilterPrivateNoCommand, manage_email, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["tags"]]) & FilterPrivateNoCommand, manage_tags, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["main_photo"]]) & FilterPrivateNoCommand, manage_main_photo, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["job_region"]]) & FilterPrivateNoCommand, manage_job_region, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["branch"]]) & FilterPrivateNoCommand, manage_branch, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["status"]]) & FilterPrivateNoCommand, manage_status, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["groups"]]) & FilterPrivateNoCommand, manage_groups, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["needs"]]) & FilterPrivateNoCommand, manage_needs, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["sport"]]) & FilterPrivateNoCommand, manage_sport, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["hobby"]]) & FilterPrivateNoCommand, manage_hobby, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["offers"]]) & FilterPrivateNoCommand, manage_offers, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["social_nets"]]) & FilterPrivateNoCommand, manage_social_nets, run_async=True),
                       MessageHandler(Filters.text([PROF_MENU["referes"]]) & FilterPrivateNoCommand, manage_referes, run_async=True),
                      

                       MessageHandler(Filters.text(BACK["back"]) & FilterPrivateNoCommand, stop_conversation, run_async=True),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank, run_async=True)
                      ],
            "choose_action_fio":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_fio_action, run_async=True)],
            "choose_action_phone":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_phone_action, run_async=True)],
            "choose_action_about":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_about_action, run_async=True)],
            "choose_action_citi":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_citi_action, run_async=True)],
            "choose_action_company":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_company_action, run_async=True)],
            "choose_action_job":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_job_action, run_async=True)],
            "choose_action_site":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_site_action, run_async=True)],
            "choose_action_date_of_birth":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_date_of_birth_action, run_async=True)],
            "choose_action_email":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_email_action, run_async=True)],
            "choose_action_tags":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_tags_action, run_async=True)],
            "choose_action_main_photo":[MessageHandler(Filters.photo & FilterPrivateNoCommand, manage_main_photo_action, run_async=True),
                                       MessageHandler(Filters.text & FilterPrivateNoCommand, manage_main_photo_txt_action, run_async=True)],
            "choose_action_job_region":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_job_region_action, run_async=True)],
            "select_region":[CallbackQueryHandler(process_region, run_async=True),
                             MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter, run_async=True)], 
            "choose_action_branch":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_branch_action, run_async=True)],
            "select_branch":[CallbackQueryHandler(process_branch, run_async=True),
                             MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter, run_async=True)], 
            "choose_action_needs":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_needs_action, run_async=True)],                         
            "choose_action_sport":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_sport_action, run_async=True)],
            "delete_sport":[CallbackQueryHandler(delete_sport, run_async=True),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter, run_async=True)],
            "add_sport":[CallbackQueryHandler(add_sport, run_async=True),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter, run_async=True)],                           
            "choose_action_hobby":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_hobby_action, run_async=True)],
            "delete_hobby":[CallbackQueryHandler(delete_hobby, run_async=True),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter, run_async=True)],
            "add_hobby":[CallbackQueryHandler(add_hobby, run_async=True),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter, run_async=True)],                           
            "choose_action_offers":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_offers_action, run_async=True)],
            "delete_offers":[CallbackQueryHandler(delete_offers, run_async=True),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter, run_async=True)],
            "add_offers":[MessageHandler((Filters.text|Filters.audio|Filters.document|Filters.photo|
                          Filters.video|Filters.video_note|Filters.voice) & FilterPrivateNoCommand, add_offers, run_async=True)],
            "choose_action_social_nets":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_social_nets_action, run_async=True)], 
            "delete_social_nets":[CallbackQueryHandler(delete_social_nets, run_async=True),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter, run_async=True)],
            "add_social_nets":[MessageHandler((Filters.text|Filters.entity(MessageEntity.ALL_TYPES)) & FilterPrivateNoCommand, add_social_nets, run_async=True)], 
            "choose_action_referes":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_referes_action, run_async=True)],
            "delete_referes":[CallbackQueryHandler(delete_referes, run_async=True),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter, run_async=True)],
            "add_referes":[MessageHandler(Filters.text & FilterPrivateNoCommand, add_referes, run_async=True)],
            "select_referes":[CallbackQueryHandler(select_referes, run_async=True),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter, run_async=True)],

        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private, run_async=True),
                   CommandHandler('start', stop_conversation, Filters.chat_type.private, run_async=True)]
    )
    dp.add_handler(conv_handler)   
    pass