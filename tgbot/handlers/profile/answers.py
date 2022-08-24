
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
DEL_SKIP = {"del":"Удалить", "skip":"Пропустить"}
ADD_DEL_SKIP = {"add":"Добавить", "del":"Удалить", "skip":"Пропустить"}
BACK = {"back":"Вернуться в основное меню"} #
BACK_PROF = {"back":"Вернуться в основное меню профиля"} #

START_MENU ={
            "personal_info": "Личная информация", #
            "busines_info": "Бизнес информация",  # 
            "about_info":"О себе",
            "referes":"Рекомендатели",#
            "offers":"Предложения",
            "needs":"Потребности",#
            "view_profile":"Посмотреть профиль",#
            "view_rating":"Рейтинг",#
            }

PERSONAL_MENU ={
                "fio":"Ф.И.О", #
                "email":"e-mail", #
                "telefon":"Телефон", #
                "date_of_birth":"Дата рождения",  # 
                "main_photo":"Фотография",
                "status":"Статус",#
                "groups":"Группы",#
                }
BUSINES_MENU ={
                "company":"Компания", #
                "segment":"Сегмент", #
                "turnover":"Оборот", #
                "job":"Должность", #
                "branch":"Отрасль", #
                "inn":"ИНН", #
                "citi":"Город", #
                "job_region":"Регион присутствия",#
                "site":"Web сайт", #
}
ABOUT_MENU ={
                "about":"Коротко себе", #
                "sport":"Спорт",#
                "hobby":"Хобби",#
                "social_nets":"Соц. сети",#
                "tags":"Тэги", #
}

def make_keyboard_start_menu():
    return make_keyboard(START_MENU,"usual",2,None,BACK)

def make_keyboard_pers_menu():
    return make_keyboard(PERSONAL_MENU,"usual",4,None,BACK_PROF)

def make_keyboard_busines_menu():
    return make_keyboard(BUSINES_MENU,"usual",4,None,BACK_PROF)

def make_keyboard_about_menu():
    return make_keyboard(ABOUT_MENU,"usual",4,None,BACK_PROF)