from django.db import models
from tgbot.models import User, tgGroups, Status
from tgbot.utils import mystr

class Partnes(models.Model):
    short_name = models.CharField("Краткое название",max_length=100, null=False, blank=False)
    full_name = models.CharField("Полное наименование", max_length=256, null=True, blank=True)
    email = models.EmailField("E-mail", max_length=100, null=True, blank=True)
    tg_id = models.BigIntegerField("Telegramm ID", null=True, blank=True)

    def __str__(self):
        return self.short_name
    class Meta:
        verbose_name = 'Партнер'
        verbose_name_plural = 'Партнеры'

class SpecialOffers(models.Model):
    partner = models.ForeignKey(Partnes, on_delete=models.CASCADE, verbose_name="Партнер", blank=True, null = True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", blank=True, null = True)
    name = models.CharField("Название предложения",max_length=100, null=False, blank=False)
    text = models.TextField("Описание предложения", null=True, blank=True)
    valid_until = models.DateField("Действует до", blank=True, null=True)
    confirmed = models.BooleanField("Подтвержден", default=False)
    sending_groups = models.ManyToManyField(tgGroups, verbose_name="Группы для рассылки", blank=True)
    file = models.FileField("Фото/Видео", blank=True, null=True, upload_to="advert")
    file_id = models.CharField("file_id", unique=False, max_length=255, blank=True, null = True)
    
    def __str__(self):
        kontrag = self.partner if self.partner else self.user
        return f"От '{kontrag}': {self.name}"
    def show_groups(self)->str:
        res = ", ".join([group.name for group in self.sending_groups.all()])
        return res    
    show_groups.short_description = 'Отсылается в группы'

    class Meta:
        verbose_name = 'Специальное предложение'
        verbose_name_plural = 'Специальные предложения'

class SpecialOffersDates(models.Model):
    offer = models.ForeignKey(SpecialOffers, on_delete=models.CASCADE, verbose_name="Спец. предложение",null=False, blank=False)
    offer_date = models.DateField("Дата отправки", blank=False, null=False)
    sended = models.BooleanField("Отослан", default=False)
    class Meta:
        verbose_name_plural = 'Даты отправки предложений' 
        verbose_name = 'Дата отправки предложения' 
        ordering = ["offer", "offer_date"]

class SpecialOffersDiscounts(models.Model):
    offer = models.ForeignKey(SpecialOffers, on_delete=models.CASCADE, verbose_name="Спец. предложение",null=False, blank=False)
    for_status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Для статуса",null=False, blank=False)
    discount = models.IntegerField("Скидка, %",null=False, blank=False)
    class Meta:
        verbose_name_plural = 'Скидки для предложения' 
        verbose_name = 'Скидка для предложения' 
        ordering = ["offer"]

class SOUserRequests(models.Model):
    offer = models.ForeignKey(SpecialOffers, on_delete=models.CASCADE, verbose_name="Спец. предложение",null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь",null=False, blank=False)
    for_status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Для статуса",null=False, blank=False)
    discount = models.IntegerField("Скидка, %",null=False, blank=False)
    sended_to_partner = models.BooleanField("Отослан", default=False)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    discount_code = models.CharField("Код скидки",max_length=20, null=False, blank=False)
    
    def __str__(self):
        return f"{self.offer.name} скидка {self.discount}% до {mystr(self.offer.valid_until)}"
    
    class Meta:
        verbose_name_plural = 'Запросы на предложения' 
        verbose_name = 'Запрос на предложение' 
        ordering = ["created_at","offer"]