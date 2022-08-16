from tgbot.models import Status, MessageTemplates
from sheduler.models import TaskTypes, Tasks
from events.models import EventTypes
import datetime

# create statuses
status_set = Status.objects.filter(code = "admin")
if status_set.count() == 0:
    status = Status(code = "admin", name = "Администратор") 
    status.save()
status_set = Status.objects.filter(code = "club_resident")
if status_set.count() == 0:
    status = Status(code = "club_resident", name = "Резидент закрытого клуба") 
    status.save()
status_set = Status.objects.filter(code = "community_resident")
if status_set.count() == 0:
    status = Status(code = "community_resident", name = "Резидент сообщества") 
    status.save()
status_set = Status.objects.filter(code = "group_member")
if status_set.count() == 0:
    status = Status(code = "group_member", name = "Участник группы") 
    status.save()

#create Tasks
task_types_set = TaskTypes.objects.filter(code = "daily")
if task_types_set.count() == 0:
    task_type_daily = TaskTypes(code = "daily", name = "Ежедневное задание")
    task_type_daily.save()
else:
    task_type_daily = task_types_set[0]

task_types_set = TaskTypes.objects.filter(code = "repeat")
if len(task_types_set) == 0:
    task_type_repeat = TaskTypes(code = "repeat", name = "Повторяемое задание")
    task_type_repeat.save()
else:
    task_type_repeat = task_types_set[0]

task_set = Tasks.objects.filter(code = "random_coffe")
if task_set.count() == 0:
    task_coffe = Tasks()
    task_coffe.code = "random_coffe"
    task_coffe.name =  "Random coffe"
    task_coffe.task_type = task_type_daily # тип - недельное
    task_coffe.time = datetime.time(9, 00, 00) # время запуска 9:00
    task_coffe.mon = True # по понедельникам
    task_coffe.is_active = True # активно 
    task_coffe.save()  

task_set = Tasks.objects.filter(code = "send_messages")
if task_set.count() == 0:
    task_send_messages = Tasks()
    task_send_messages.code = "send_messages"
    task_send_messages.name =  "Рассылка сообщений"
    task_send_messages.task_type = task_type_repeat # тип - Повторяемое
    task_send_messages.interval = 10 # повторяется с интервалом 10 сек
    task_send_messages.is_active = True # активно 
    task_send_messages.save()       
else:
    task_send_messages = task_set[0]

# create message templates
random_coffe_template_set = MessageTemplates.objects.filter(code = "random_coffe")
if random_coffe_template_set.count() == 0:
    random_coffe_template = MessageTemplates(code = "random_coffe", name = "Шаблон для сообщений Random coffe")
    random_coffe_template.text = "Random coffe текст сообщения"
    random_coffe_template.save()

# create EventTypes
event_type_set = EventTypes.objects.filter(code = "close")
if event_type_set.count() == 0:
    event_type = EventTypes(code = "close", name = "Закрытое") 
    event_type.save()
event_type_set = EventTypes.objects.filter(code = "club")
if event_type_set.count() == 0:
    event_type = EventTypes(code = "club", name = "Клубное") 
    event_type.save()
event_type_set = EventTypes.objects.filter(code = "open")
if event_type_set.count() == 0:
    event_type = EventTypes(code = "open", name = "Открытое") 
    event_type.save()
    

    
