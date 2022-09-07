from django.db import models
from tgbot.models import User, Config

class Tasks(models.Model):
    code = models.CharField("Код задания", unique=True, max_length=150, blank=False)
    name = models.CharField("Имя задания", unique=True, max_length=150, blank=False)
    date = models.DateField("Дата запуска", blank=True, null=True)
    time = models.TimeField("Время запуска", blank=True, null=True)
    # Ежедневный запуск
    mon = models.BooleanField("пн", default=False)
    tue = models.BooleanField("вт", default=False)
    wed = models.BooleanField("ср", default=False)
    thu = models.BooleanField("чт", default=False)
    fri = models.BooleanField("пт", default=False)
    sat = models.BooleanField("сб", default=False)
    san = models.BooleanField("вс", default=False)
    # Ежемесячный запуск
    day = models.IntegerField("День месяца", null = True, blank=True)
    # Постоянное задание
    interval = models.IntegerField("интервал выполнения, сек.", null = True, blank=True)
    is_active = models.BooleanField("Активно", default=False)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        #Ставим метку перестартовать задачи при изменении параметров задачи
        restart_tasks = Config.objects.filter(param_name = "restart_tasks").first()
        if not restart_tasks:
            restart_tasks = Config()
            restart_tasks.param_name = "restart_tasks"
        restart_tasks.param_val = "True"
        restart_tasks.save()
        super(Tasks, self).save(*args, **kwargs)

    def getdays(self):
        res = []
        if self.mon: res.append(0)
        if self.tue: res.append(1)
        if self.wed: res.append(2)
        if self.thu: res.append(3)
        if self.fri: res.append(4)
        if self.sat: res.append(5)
        if self.san: res.append(6)
        return tuple(res)

    class Meta:
        verbose_name_plural = 'Задания' 
        verbose_name = 'Задание' 
        ordering = ['name']

class MessagesToSend(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver", verbose_name="Получатель", blank=True, null=True)    
    receiver_user_id = models.BigIntegerField("ID пользователя", blank=True, null=True)
    text = models.TextField("Текст сообщения", null=False, blank=False)
    created_at = models.DateTimeField("Создано в", auto_now_add=True)
    sended_at = models.DateTimeField("Отослано в", blank=True, null=True)
    sended = models.BooleanField("Отослано", default=False)
    file = models.FileField("Файл", blank=True, null=True, upload_to="messages")
    file_id = models.CharField("file_id", unique=False, max_length=255, blank=True, null = True)
    reply_markup = models.JSONField(blank=True, null = True) # здесь хранится словарь с описанием клавиатуры прикрепляемой к сообщению
    comment = models.TextField("Комментарий", blank=True, null=True)
    def __str__(self):
        return self.text
    class Meta:
        verbose_name_plural = 'Сообщения к отсылке' 
        verbose_name = 'Сообщение к отсылке' 
        ordering = ['created_at']


class MessageTemplates(models.Model):
    code = models.CharField("Код", max_length=256, null=False, blank=False)
    name = models.CharField("Название", max_length=256, null=False, blank=False)
    text = models.TextField("Текст сообщения", blank=False)
    file = models.FileField("Файл", blank=True, null=True, upload_to="templates")
    file_id = models.CharField("file_id", unique=False, max_length=255, blank=True, null = True)
    

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Шаблоны сообщений' 
        verbose_name = 'Шаблон сообщения' 
        ordering = ['code']