import datetime
from django.db import models
from tgbot.models import User, tgGroups

class MessageStatistic(models.Model):
    group = models.ForeignKey(tgGroups, on_delete=models.CASCADE, verbose_name="Группа")
    messages = models.IntegerField("Число сообщений в группе", default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    date = models.DateField("Дата", default=datetime.date.today)
    def __str__(self):
        return  str(self.user) + "; " + str(self.group) + " = " + str(self.messages)
    class Meta:
        verbose_name_plural = 'Статистика сообщений' 
        verbose_name = 'Сообщений в группе' 
        ordering = ['user','group']
