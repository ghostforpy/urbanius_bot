
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
                "job":"Должность", #
                "branch":"Отрасль", #
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

