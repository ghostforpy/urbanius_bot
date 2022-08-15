from django.db import models
from tgbot.models import User, tgGroups,Status

class EventTypes(models.Model):
    code = models.CharField("Код типа мероприятия", unique=True, max_length=30, blank=False)
    name = models.CharField("Тип мероприятия", max_length=150, blank=False)
    for_status = models.ManyToManyField(Status, blank=True, verbose_name="Для пользователей со статусом")
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Типы мероприятий' 
        verbose_name = 'Тип мероприятия' 
        ordering = ['name']

class Events(models.Model):
    date = models.DateField("Дата мероприятия", blank=False, null=False)
    time = models.TimeField("Время мероприятия", blank=True, null=True)
    name = models.CharField("Название мероприятия", max_length=150, blank=False)
    description = models.TextField("Описание", null=True, blank=True)
    place = models.CharField("Место проведения", unique=False, max_length=150, blank=True, null = True)
    event_link = models.URLField("Страница события", blank=True, null = True)
    regisration_link = models.URLField("Страница формы регистрации", blank=True, null = True)
    file = models.FileField("Фото/Видео", blank=True, null=True, upload_to="events")
    type = models.ForeignKey(EventTypes, on_delete=models.PROTECT, verbose_name="Тип мероприятия",null=True, blank=False)
    def __str__(self):
        return  str(self.date) + " - " + str(self.name)
    class Meta:
        verbose_name_plural = 'Мероприятия' 
        verbose_name = 'Мероприятие' 
        ordering = ['date','time']
