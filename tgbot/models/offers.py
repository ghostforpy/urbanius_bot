# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

class Offers(models.Model):
    offer = models.TextField("Суть предложения", blank = True, null = True)
    image = models.FileField("Файл", blank=True, upload_to="offers")
    image_id = models.CharField("file_id", unique=False, max_length=255, blank=True, null = True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return  self.offer
    class Meta:
        verbose_name_plural = 'Предложения' 
        verbose_name = 'Предложение' 
        ordering = ['user']