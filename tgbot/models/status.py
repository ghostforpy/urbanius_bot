from django.db import models

class Status(models.Model):
    code = models.CharField("Код", max_length=50, blank=True)
    name = models.CharField("Статус пользователя", unique=True, max_length=150, blank=False)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Статусы пользователя' 
        verbose_name = 'Статус пользователя' 
        ordering = ['name']