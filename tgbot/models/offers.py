# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

class Offers(models.Model):
    DECISION_CHOISES = [
        ("accepted", "Принято"),
        ("rejected", "Отклонено"),
        ("under_consideration", "На рассмотрении"),
    ]
    offer = models.TextField("Суть предложения", blank = True, null = True)
    image = models.FileField("Файл", blank=True, upload_to="offers")
    image_id = models.CharField("file_id", unique=False, max_length=255, blank=True, null = True)
    user = models.ForeignKey(
        "User", 
        on_delete=models.CASCADE, 
        verbose_name="Пользователь",
        related_name="offers"
    )
    decision = models.CharField(
        _("Решение пользователя"),
        max_length=50,
        default="under_consideration",
        choices=DECISION_CHOISES
    )
    from_user = models.ForeignKey(
        "User", 
        on_delete=models.CASCADE, 
        verbose_name="Инициатор предложения",
        related_name="made_offers",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True, blank=True, null=True)
    create_done = models.BooleanField("Создание закончено", default=False)

    def __str__(self):
        return "Предложение " + str(self.from_user) + " к " + str(self.user)

    class Meta:
        verbose_name_plural = 'Предложения' 
        verbose_name = 'Предложение' 
        ordering = ['id', 'user']