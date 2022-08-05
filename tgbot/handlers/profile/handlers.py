import os
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters,
    ConversationHandler,
)
from telegram import InputMediaDocument

from django.conf import settings
from tgbot.handlers.profile.messages import *
from tgbot.handlers.profile.answers import *
from tgbot.handlers.main.answers import START_MENU_FULL
import tgbot.models as mymodels
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start
from tgbot.handlers.utils import send_message
from tgbot.utils import extract_user_data_from_update, mystr, is_date, is_email, get_uniq_file_name
from tgbot.handlers.files import _get_file_id
# Возврат к главному меню в исключительных ситуациях
def prof_stop(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    command_start(update, context)
    return ConversationHandler.END

# Временная заглушка
def blank(update: Update, context: CallbackContext):
    pass

# Возврат к главному меню по кнопке
def back_to_start(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    command_start(update, context)
    return ConversationHandler.END

def bad_callback_enter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(EMPTY,"usual",2))

# Начало работы с профилем
def start_manage_profile(update: Update, context: CallbackContext):
    userdata = extract_user_data_from_update(update)
    user = mymodels.User.get_user_by_username_or_user_id(userdata["user_id"])
    context.user_data["user"] = user    
    update.message.reply_text(PROF_HELLO, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"

# Обработчик фамилиии
def manage_fio(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    fio = " ".join([mystr(user.last_name), mystr(user.first_name), mystr(user.sur_name)])
    update.message.reply_text(ASK_FIO.format(fio), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_fio"
  
def manage_fio_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
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
    user = context.user_data["user"]
    update.message.reply_text(ASK_PHONE.format(user.telefon), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_phone"

def manage_phone_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
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
    user = context.user_data["user"]
    update.message.reply_text(ASK_ABOUT.format(user.about), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_about"

def manage_about_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
        user.telefon = update.message.text
        user.save()
        text = "Информация 'О себе' изменена"
    else:
        text = "Информация 'О себе' не изменена"
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"
#-------------------------------------------  
# Обработчик Город
def manage_citi(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    update.message.reply_text(ASK_CITI.format(user.citi), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_citi"

def manage_citi_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
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
    user = context.user_data["user"]
    update.message.reply_text(ASK_COMPANY.format(user.company), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_company"

def manage_company_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
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
    user = context.user_data["user"]
    update.message.reply_text(ASK_JOB.format(user.job), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_job"

def manage_job_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
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
    user = context.user_data["user"]
    update.message.reply_text(ASK_SITE.format(user.site), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_site"

def manage_site_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
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
    user = context.user_data["user"]
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
        user = context.user_data["user"]
        user.date_of_birth = date
        user.save()
        text = "День рождения изменен"
        
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"
#-------------------------------------------  
# Обработчик e-mail
def manage_email(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    update.message.reply_text(ASK_EMAIL.format(user.email), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_email"

def manage_email_action(update: Update, context: CallbackContext):
    email = is_email(update.message.text)
    text = ""
    if update.message.text == SKIP["skip"]:        
        text = "e-mail рождения не изменен"
    elif not(email): # ввели неверную email
        update.message.reply_text(BAD_EMAIL, make_keyboard(SKIP,"usual",1))
        return 
    else:
        user = context.user_data["user"]
        user.email = email
        user.save()
        text = "e-mail рождения изменен"
        
    update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"
#-------------------------------------------  
# Обработчик Теги
def manage_tags(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    update.message.reply_text(ASK_TAGS.format(user.tags), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_tags"

def manage_tags_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = context.user_data["user"]
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
    user = context.user_data["user"]
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
    user = context.user_data["user"]
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
    user = context.user_data["user"]
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
        all_regions = mymodels.get_dict(mymodels.JobRegions,"pk","name")
        update.message.reply_text("Выберите регион", reply_markup=make_keyboard(all_regions,"inline",4))
        return "select_region"
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(CHANGE_SKIP,"usual",2))

def process_region(update: Update, context: CallbackContext):
    user = context.user_data["user"]
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
    user = context.user_data["user"]
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
        all_branchs = mymodels.get_dict(mymodels.Branch,"pk","name")
        update.message.reply_text("Выберите отрасль", reply_markup=make_keyboard(all_branchs,"inline",4))
        return "select_branch"
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(CHANGE_SKIP,"usual",2))

def process_branch(update: Update, context: CallbackContext):
    user = context.user_data["user"]
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
    user = context.user_data["user"]
    update.message.reply_text(SAY_STATUS.format(user.status), reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"

#-------------------------------------------  
# Обработчик Группы
def manage_groups(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    all_groups = mymodels.get_model_text(mymodels.UsertgGroups,["NN","group"], user)
    update.message.reply_text(SAY_GROUPS.format(str(all_groups)), reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
    return "working"

#-------------------------------------------  
# Обработчик потребности
def manage_needs(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    all_needs = mymodels.get_model_text(mymodels.UserNeeds,["NN","need"], user)
    update.message.reply_text(ASK_NEEDS.format(str(all_needs)), reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))
    return "choose_action_needs"

def manage_needs_action(update: Update, context: CallbackContext):
    user = context.user_data["user"]    
    if update.message.text == ADD_DEL_SKIP["skip"]:        
        text = "Потребности не изменены"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    elif update.message.text == ADD_DEL_SKIP["del"]:
        update.message.reply_text("Удаление потребностей", reply_markup=make_keyboard(EMPTY,"usual",1))
        all_needs = mymodels.get_dict(mymodels.UserNeeds,"pk","NN", user)
        all_needs_txt = mymodels.get_model_text(mymodels.UserNeeds,["NN","need"], user)
        text = all_needs_txt + "Введите номер удаляемой строки"
        update.message.reply_text(text, reply_markup=make_keyboard(all_needs,"inline",8,None,FINISH))
        return "delete_need"
    elif update.message.text == ADD_DEL_SKIP["add"]:
        all_user_needs_txt = mymodels.get_model_text(mymodels.UserNeeds,["NN","need"], user)
        all_needs_txt = mymodels.get_model_text(mymodels.Needs,["NN","name"])
        all_needs = mymodels.get_dict(mymodels.Needs,"pk","NN")
        update.message.reply_text("Добавление потребностей", reply_markup=make_keyboard(EMPTY,"usual",1))
        text = "Возможные потребности:\n"
        text += all_needs_txt
        text += "\nВаши потребности:\n"
        text += all_user_needs_txt
        text += "Введите номер добавляемой потребности"
        update.message.reply_text(text, reply_markup=make_keyboard(all_needs,"inline",8,None,FINISH))
        return "add_need"
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))

def delete_need(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "finish":
        all_needs_txt = mymodels.get_model_text(mymodels.UserNeeds,["NN","need"], user)
        query.edit_message_text(text=all_needs_txt)
        text = "Удаление потребностей завершено"
        reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "working"
    else:
        need = mymodels.UserNeeds.objects.get(pk=int(variant))
        need.delete()
        all_needs = mymodels.get_dict(mymodels.UserNeeds,"pk","NN", user)
        if len(all_needs) == 0:
            all_needs_txt = "Все потребности удалены"
            query.edit_message_text(text=all_needs_txt)
            text = "Удаление потребностей завершено"
            reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
            send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
            return "working"
        else:           
            all_needs_txt = mymodels.get_model_text(mymodels.UserNeeds,["NN","need"], user)
            text = all_needs_txt + "Введите номер удаляемой строки"
            query.edit_message_text(text, reply_markup=make_keyboard(all_needs,"inline",8,None,FINISH))

def add_need(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "finish":
        all_needs_txt = mymodels.get_model_text(mymodels.UserNeeds,["NN","need"], user)
        query.edit_message_text(text=all_needs_txt)
        text = "Добавление потребностей завершено"
        reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "working"
    else:
        need = mymodels.Needs.objects.get(pk=int(variant))
        user_needs =  mymodels.UserNeeds.objects.filter(need = need, user = user)
        if len(user_needs) == 0:
            user_need = mymodels.UserNeeds(need = need, user = user)
            user_need.save()
            all_user_needs_txt = mymodels.get_model_text(mymodels.UserNeeds,["NN","need"], user)
            all_needs_txt = mymodels.get_model_text(mymodels.Needs,["NN","name"])
            all_needs = mymodels.get_dict(mymodels.Needs,"pk","NN")
            text = "Возможные потребности:\n"
            text += all_needs_txt
            text += "\nВаши потребности:\n"
            text += all_user_needs_txt
            text += "Введите номер добавляемой потребности"
            query.edit_message_text(text, reply_markup=make_keyboard(all_needs,"inline",8,None,FINISH))
        
#-------------------------------------------  
# Обработчик Спорта
def manage_sport(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    all_sport = mymodels.get_model_text(mymodels.UserSport,["NN","sport"], user)
    update.message.reply_text(ASK_SPORT.format(str(all_sport)), reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))
    return "choose_action_sport"

def manage_sport_action(update: Update, context: CallbackContext):
    user = context.user_data["user"]    
    if update.message.text == ADD_DEL_SKIP["skip"]:        
        text = "Виды спорта не изменены"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    elif update.message.text == ADD_DEL_SKIP["del"]:
        update.message.reply_text("Удаление видов спорта", reply_markup=make_keyboard(EMPTY,"usual",1))
        all_sport = mymodels.get_dict(mymodels.UserSport,"pk","NN", user)
        all_sport_txt = mymodels.get_model_text(mymodels.UserSport,["NN","sport"], user)
        text = all_sport_txt + "Введите номер удаляемой строки"
        update.message.reply_text(text, reply_markup=make_keyboard(all_sport,"inline",8,None,FINISH))
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
    user = context.user_data["user"]
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
        all_sport = mymodels.get_dict(mymodels.UserSport,"pk","NN", user)
        if len(all_sport) == 0:
            all_sport_txt = "Все виды спорта удалены"
            query.edit_message_text(text=all_sport_txt)
            text = "Удаление видов спорта завершено"
            reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
            send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
            return "working"
        else:           
            all_sport_txt = mymodels.get_model_text(mymodels.UserSport,["NN","sport"], user)
            text = all_sport_txt + "Введите номер удаляемой строки"
            query.edit_message_text(text, reply_markup=make_keyboard(all_sport,"inline",8,None,FINISH))

def add_sport(update: Update, context: CallbackContext):
    user = context.user_data["user"]
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
    user = context.user_data["user"]
    all_hobby = mymodels.get_model_text(mymodels.UserHobby,["NN","hobby"], user)
    update.message.reply_text(ASK_HOBBY.format(str(all_hobby)), reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))
    return "choose_action_hobby"

def manage_hobby_action(update: Update, context: CallbackContext):
    user = context.user_data["user"]    
    if update.message.text == ADD_DEL_SKIP["skip"]:        
        text = "Виды хобби не изменены"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    elif update.message.text == ADD_DEL_SKIP["del"]:
        update.message.reply_text("Удаление видов хобби", reply_markup=make_keyboard(EMPTY,"usual",1))
        all_hobby = mymodels.get_dict(mymodels.UserHobby,"pk","NN", user)
        all_hobby_txt = mymodels.get_model_text(mymodels.UserHobby,["NN","hobby"], user)
        text = all_hobby_txt + "Введите номер удаляемой строки"
        update.message.reply_text(text, reply_markup=make_keyboard(all_hobby,"inline",8,None,FINISH))
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
    user = context.user_data["user"]
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
        all_hobby = mymodels.get_dict(mymodels.UserHobby,"pk","NN", user)
        if len(all_hobby) == 0:
            all_hobby_txt = "Все виды хобби удалены"
            query.edit_message_text(text=all_hobby_txt)
            text = "Удаление видов хобби завершено"
            reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
            send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
            return "working"
        else:           
            all_hobby_txt = mymodels.get_model_text(mymodels.UserHobby,["NN","hobby"], user)
            text = all_hobby_txt + "Введите номер удаляемой строки"
            query.edit_message_text(text, reply_markup=make_keyboard(all_hobby,"inline",8,None,FINISH))

def add_hobby(update: Update, context: CallbackContext):
    user = context.user_data["user"]
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
    user = context.user_data["user"]
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
    user = context.user_data["user"]    
    if update.message.text == ADD_DEL_SKIP["skip"]:        
        text = "Ваши предложения не изменены"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    elif update.message.text == ADD_DEL_SKIP["del"]:
        update.message.reply_text("Удаление предложений", reply_markup=make_keyboard(EMPTY,"usual",1))
        all_offers = mymodels.get_dict(mymodels.Offers,"pk","NN", user)
        all_offers_txt = mymodels.get_model_text(mymodels.Offers,["NN","offer","image"], user)
        text = all_offers_txt + "Введите номер удаляемой строки"
        update.message.reply_text(text, reply_markup=make_keyboard(all_offers,"inline",8,None,FINISH))
        return "delete_offers"
    elif update.message.text == ADD_DEL_SKIP["add"]:
        all_offers_txt = mymodels.get_model_text(mymodels.Offers,["NN","offer","image"], user)
        text = ADD_OFFERS+"\nВаши предложения \n" + all_offers_txt        
        update.message.reply_text(text, reply_markup=make_keyboard(FINISH,"usual",1))
        return "add_offers"
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))

def delete_offers(update: Update, context: CallbackContext):
    user = context.user_data["user"]
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
        all_offers = mymodels.get_dict(mymodels.Offers,"pk","NN", user)
        if len(all_offers) == 0:
            all_offers_txt = "Все предложения удалены"
            query.edit_message_text(text=all_offers_txt)
            text = "Удаление предложений завершено"
            reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK) 
            send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
            return "working"
        else:           
            all_offers_txt = mymodels.get_model_text(mymodels.Offers,["NN","offer","image"], user)
            text = all_offers_txt + "Введите номер удаляемой строки"
            query.edit_message_text(text, reply_markup=make_keyboard(all_offers,"inline",8,None,FINISH))

def add_offers(update: Update, context: CallbackContext):
    user = context.user_data["user"]
    if update.message.text == FINISH["finish"]:        
        text = "Завершено добавление предложений"
        update.message.reply_text(text, reply_markup=make_keyboard(PROF_MENU,"usual",4,None,BACK))
        return "working"
    if update.message.text != None:
        text = update.message.text
    elif update._effective_message.caption != None:
        text = update._effective_message.caption
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



def setup_dispatcher_prof(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор
        entry_points=[MessageHandler(Filters.text(START_MENU_FULL["profile"]) & FilterPrivateNoCommand, start_manage_profile)],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[
                       MessageHandler(Filters.text(PROF_MENU["fio"]) & FilterPrivateNoCommand, manage_fio),
                       MessageHandler(Filters.text(PROF_MENU["telefon"]) & FilterPrivateNoCommand, manage_phone),
                       MessageHandler(Filters.text(PROF_MENU["about"]) & FilterPrivateNoCommand, manage_about),
                       MessageHandler(Filters.text(PROF_MENU["citi"]) & FilterPrivateNoCommand, manage_citi),
                       MessageHandler(Filters.text(PROF_MENU["company"]) & FilterPrivateNoCommand, manage_company),
                       MessageHandler(Filters.text(PROF_MENU["job"]) & FilterPrivateNoCommand, manage_job),
                       MessageHandler(Filters.text(PROF_MENU["site"]) & FilterPrivateNoCommand, manage_site),
                       MessageHandler(Filters.text(PROF_MENU["date_of_birth"]) & FilterPrivateNoCommand, manage_date_of_birth),
                       MessageHandler(Filters.text(PROF_MENU["email"]) & FilterPrivateNoCommand, manage_email),
                       MessageHandler(Filters.text(PROF_MENU["tags"]) & FilterPrivateNoCommand, manage_tags),
                       MessageHandler(Filters.text(PROF_MENU["main_photo"]) & FilterPrivateNoCommand, manage_main_photo),
                       MessageHandler(Filters.text(PROF_MENU["job_region"]) & FilterPrivateNoCommand, manage_job_region),
                       MessageHandler(Filters.text(PROF_MENU["branch"]) & FilterPrivateNoCommand, manage_branch),
                       MessageHandler(Filters.text(PROF_MENU["status"]) & FilterPrivateNoCommand, manage_status),
                       MessageHandler(Filters.text(PROF_MENU["groups"]) & FilterPrivateNoCommand, manage_groups),
                       MessageHandler(Filters.text(PROF_MENU["needs"]) & FilterPrivateNoCommand, manage_needs),
                       MessageHandler(Filters.text(PROF_MENU["sport"]) & FilterPrivateNoCommand, manage_sport),
                       MessageHandler(Filters.text(PROF_MENU["hobby"]) & FilterPrivateNoCommand, manage_hobby),
                       MessageHandler(Filters.text(PROF_MENU["offers"]) & FilterPrivateNoCommand, manage_offers),

                       MessageHandler(Filters.text(BACK["back"]) & FilterPrivateNoCommand, back_to_start),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ],
            "choose_action_fio":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_fio_action)],
            "choose_action_phone":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_phone_action)],
            "choose_action_about":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_about_action)],
            "choose_action_citi":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_citi_action)],
            "choose_action_company":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_company_action)],
            "choose_action_job":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_job_action)],
            "choose_action_site":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_site_action)],
            "choose_action_date_of_birth":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_date_of_birth_action)],
            "choose_action_email":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_email_action)],
            "choose_action_tags":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_tags_action)],
            "choose_action_main_photo":[MessageHandler(Filters.photo & FilterPrivateNoCommand, manage_main_photo_action),
                                       MessageHandler(Filters.text & FilterPrivateNoCommand, manage_main_photo_txt_action)],
            "choose_action_job_region":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_job_region_action)],
            "select_region":[CallbackQueryHandler(process_region),
                             MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter)], 
            "choose_action_branch":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_branch_action)],
            "select_branch":[CallbackQueryHandler(process_branch),
                             MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter)], 
            "choose_action_needs":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_needs_action)],
            "delete_need":[CallbackQueryHandler(delete_need),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter)],
            "add_need":[CallbackQueryHandler(add_need),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter)],                           
            "choose_action_sport":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_sport_action)],
            "delete_sport":[CallbackQueryHandler(delete_sport),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter)],
            "add_sport":[CallbackQueryHandler(add_sport),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter)],                           
            "choose_action_hobby":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_hobby_action)],
            "delete_hobby":[CallbackQueryHandler(delete_hobby),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter)],
            "add_hobby":[CallbackQueryHandler(add_hobby),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter)],                           
            "choose_action_offers":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_offers_action)],
            "delete_offers":[CallbackQueryHandler(delete_offers),
                           MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter)],
            "add_offers":[MessageHandler((Filters.text|Filters.audio|Filters.document|Filters.photo|
                          Filters.video|Filters.video_note|Filters.voice) & FilterPrivateNoCommand, add_offers)], 

        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', prof_stop, Filters.chat_type.private)]
    )
    dp.add_handler(conv_handler)   
    pass