
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

START_MENU = {
            "personal_info": "Личная информация", #
            "busines_info": "Бизнес информация",  # 
            # "about_info":"О себе",
            # "referes":"Рекомендатели",#
            "needs":"Потребности",#
            "offers":"Предложения",
            "view_profile":"Посмотреть профиль",#
            "business_branch" : "Сегмент бизнеса",
            # "view_rating":"Рейтинг",#
            }

PERSONAL_MENU ={
                "first_name":"Имя", #
                "sur_name":"Отчество", #
                "last_name":"Фамилия", #
                # "email":"e-mail", #
                # "telefon":"Телефон", #
                "date_of_birth":"Дата рождения",  # 
                "main_photo":"Фотография",
                "hobby":"Хобби",
                # "status":"Статус",#
                # "groups":"Группы",#
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

NEXT = {"done": "💾 Готово"}

CREATE = {"create": "Другое"}

CANCEL_CREATE = {"cancel":"Отмена"}

def make_keyboard_start_menu():
    return make_keyboard(START_MENU,"usual",2,None,BACK)

def make_keyboard_pers_menu():
    return make_keyboard(PERSONAL_MENU,"usual",4,None,BACK_PROF)

def make_keyboard_busines_menu():
    return make_keyboard(BUSINES_MENU,"usual",4,None,BACK_PROF)

def make_keyboard_about_menu():
    return make_keyboard(ABOUT_MENU,"usual",4,None,BACK_PROF)