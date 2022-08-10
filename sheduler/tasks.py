import pytz
import datetime
from telegram.ext import JobQueue, CallbackContext
from .models import *

def remove_job_if_exists(name: str, jq: JobQueue):
    """
       Удаляет задание с заданным именем. 
       Возвращает, было ли задание удалено
    """
    current_jobs = jq.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def restarts_tasks(jq: JobQueue) -> JobQueue:
    # Создаем/обновляем задание "Random coffe"
    task_types_set = TaskTypes.objects.filter(code = "daily")
    if len(task_types_set) == 0:
        task_type_daily = TaskTypes(code = "daily", name = "Ежедневное задание")
        task_type_daily.save()
    else:
        task_type_daily = task_types_set[0]

    task_set = Tasks.objects.filter(code = "random_coffe")
    if len(task_set) == 0:
        task_coffe = Tasks()
        task_coffe.code = "random_coffe"
        task_coffe.name =  "Random coffe"
        task_coffe.task_type = task_type_daily # тип - недельное
        task_coffe.time = datetime.time(9, 00, 00) # время запуска 9:00
        task_coffe.mon = True # по понедельникам
        task_coffe.is_active = True # активно 
        task_coffe.save()       
    else:
        task_coffe = task_set[0]

    remove_job_if_exists("random_coffe", jq)
    if task_coffe.is_active:
        days = task_coffe.getdays()
        time = datetime.time(hour=task_coffe.time.hour, minute=task_coffe.time.minute, tzinfo=pytz.timezone('Europe/Moscow'))
        jq.run_daily(send_random_coffe, time, days = days, context = "random_coffe", name="random_coffe")

    # Создаем/обновляем задание "Рассылка сообщений"
    task_types_set = TaskTypes.objects.filter(code = "repeat")
    if len(task_types_set) == 0:
        task_type_repeat = TaskTypes(code = "repeat", name = "Повторяемое задание")
        task_type_repeat.save()
    else:
        task_type_repeat = task_types_set[0]

    task_set = Tasks.objects.filter(code = "send_messages")
    if len(task_set) == 0:
        task_send_messages = Tasks()
        task_send_messages.code = "send_messages"
        task_send_messages.name =  "Рассылка сообщений"
        task_send_messages.task_type = task_type_repeat # тип - Повторяемое
        task_send_messages.interval = 10 # повторяется с интервалом 10 сек
        task_send_messages.is_active = True # активно 
        task_send_messages.save()       
    else:
        task_send_messages = task_set[0]

    remove_job_if_exists("send_messages", jq)
    if task_send_messages.is_active:

        jq.run_repeating(send_sheduled_message, task_send_messages.interval, name="send_messages")

    jq.start()         
    return jq

def send_random_coffe(context: CallbackContext):
    print("Сработало задание кофе")
    pass

def send_sheduled_message(context: CallbackContext):
    print("Сработало задание рассылки")
    pass