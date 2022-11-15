
from tgbot.models import User
from tgbot.handlers.keyboard import make_keyboard

EMPTY = {}
CANCEL = {"cancel":"Отмена"}
CANCEL_SKIP = {"cancel":"Отмена","skip":"Пропустить"}
SKIP = {"skip":"Пропустить"}
OK = {"ok":"OK"}
START = {"start":"/start"}
FINISH = {"finish":"Завершить"}
YES_NO = {"yes":"Да", "no":"Нет"}
CHANGE_SKIP = {"change":"Изменить", "skip":"Пропустить"}
BACK = {"back":"Вернуться в основное меню"} 
FIND = {"find_members":{"label":"Найти участников","type":"switch_inline"}}

def make_manage_usr_btn(user_id, show_full_profile=False):
    manage_usr_btn = {"setuserrating_"+ str(user_id):"Поставить оценку",
                    #   "dating_"+ str(user_id):"Познакомиться",
                    #   "make_deal_"+ str(user_id):"Заключить сделку",
                      }
    if show_full_profile:
        manage_usr_btn["full_profile_"+ str(user_id)] = "Полный профиль"
    return manage_usr_btn

def back_to_user_btn(user_id):
    return {"back_to_user_"+ str(user_id):"Назад"}