
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

PROF_MENU = {
                "fio":"Ф.И.О", #
                "date_of_birth":"Дата рождения",  # 
                "main_photo":"Фотография",
                "telefon":"Телефон", #
                "email":"e-mail", #
                "citi":"Город", #
                "company":"Компания", #
                "job":"Должность", #
                "site":"Web сайт", #
                "tags":"Тэги", #
                "about":"О себе", #
                "job_region":"Регион присутствия",#
                "branch":"Отрасль", #
                "offers":"Предложения",#
                "social_nets":"Соц. сети",#----------
                "needs":"Потребности",#
                "sport":"Спорт",#
                "hobby":"Хобби",#
                "referes":"Рекомендатели",#----------
                "status":"Статус",#
                "groups":"Группы",#
            }
