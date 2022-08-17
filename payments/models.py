from django.db import models
from tgbot.models import User

class Payments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь",null=False, blank=False)
    price = models.DecimalField("Сумма счета", max_digits=11, decimal_places=2)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    invoice_payload = models.CharField("invoice_payload", unique=False, max_length=150, blank=True, null = True)
    provider_payment_charge_id = models.CharField("provider_payment_charge_id", unique=False, max_length=150, blank=True, null = True)
    telegram_payment_charge_id = models.CharField("telegram_payment_charge_id", unique=False, max_length=150, blank=True, null = True)
    email = models.CharField("email", unique=False, max_length=50, blank=True, null = True)
    name = models.CharField("name", unique=False, max_length=150, blank=True, null = True)
    phone_number = models.CharField("phone_number", unique=False, max_length=15, blank=True, null = True)
    total_amount = models.DecimalField("Оплачено", max_digits=11, decimal_places=2)
    def __str__(self):
        return f"{self.created_at} от пользователя {self.user} цена {self.price} руб."
    class Meta:
        verbose_name_plural = 'Платежи пользователей' 
        verbose_name = 'Платеж пользователя' 
        ordering = ['created_at','user']
