import qrcode
from django.db import models
from payments.models import Payments
from tgbot.models import User, tgGroups,Status

class EventTypes(models.Model):
    code = models.CharField("Код типа мероприятия", unique=True, max_length=30, blank=False)
    name = models.CharField("Тип мероприятия", max_length=150, blank=False)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Типы мероприятий' 
        verbose_name = 'Тип мероприятия' 
        ordering = ['name']

class EventPrices(models.Model):
    event = models.ForeignKey('Events', on_delete=models.PROTECT, verbose_name="Мероприятие",null=False, blank=False)
    for_status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Для статуса",null=False, blank=False)
    price = models.DecimalField("Стоимость мероприятия", max_digits=11, decimal_places=2)
    def __str__(self):
        return f"{self.event} для статуса {self.for_status} цена {self.price} руб."
    class Meta:
        verbose_name_plural = 'Стоимость мероприятий' 
        verbose_name = 'Стоимость мероприятия' 
        ordering = ['event']

class Events(models.Model):
    date = models.DateField("Дата мероприятия", blank=False, null=False)
    time = models.TimeField("Время мероприятия", blank=True, null=True)
    name = models.CharField("Название мероприятия", max_length=150, blank=False)
    description = models.TextField("Описание", null=True, blank=True)
    place = models.CharField("Место проведения", unique=False, max_length=150, blank=True, null = True)
    event_link = models.URLField("Страница мероприятия", blank=True, null = True)
    regisration_link = models.URLField("Страница формы регистрации", blank=True, null = True)
    file = models.FileField("Фото/Видео", blank=True, null=True, upload_to="events")
    file_id = models.CharField("file_id", unique=False, max_length=255, blank=True, null = True)
    type = models.ForeignKey(EventTypes, on_delete=models.PROTECT, verbose_name="Тип мероприятия",null=True, blank=False)
    
    def __str__(self):
        week   = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        week_day = week[self.date.weekday()]
        str_date = self.date.strftime("%d.%m.%Y")
        if self.time:
            str_time = self.time.strftime("%H:%M")
        else:
            str_time = ""        
        return  f"{week_day}, {str_date}, {str_time} - {self.name}"

    def get_price(self, user: User) -> float:
        price_set = self.eventprices_set.filter(for_status = user.status)
        price = 0
        if price_set.count() > 0:
            price = price_set[0].price
        return price

    def get_description(self) -> str:
        res = ""
        res += f"<b>{self}</b>\n"
        res += f"<b>Тип мероприятия:</b> {self.type}\n"
        res += f"<b>Описание:</b>\n{self.description}\n"
        if self.place:
            res += f"<b>Место проведения:</b>\n{self.place}\n"
        if self.event_link:
            res += f"<b>Страница мероприятия:</b>\n{self.event_link}\n"
        if self.regisration_link:
           res += f"<b>Страница регистрации:</b>\n{self.regisration_link}\n"
        return res
    
    def get_user_request(self, user: User) -> "EventRequests":
        request_set = self.eventrequests_set.filter(user = user)
        if request_set.count() > 0:
            res = price = request_set[0]
        else:
            res = None
        return res

    def get_user_info(self, user: User) -> str:
        res = ""
        price = self.get_price(user)
        if price > 0:
            res += f"<b>Стоимость участия:</b> {price} руб.\n"
        else:
            res += f"<b>Стоимость участия:</b> бесплатно\n"
        request = self.get_user_request(user)
        if request:
            res += f"<b>Оформлена заявка №: </b> {request.number}\n"
            if request.price > 0:
                res += f"<b>цена: </b> {request.price} руб.\n"
                res += "оплачена\n" if request.payed else "не оплачена\n"
            res += "подтверждена\n" if request.confirmed else "не подтверждена\n"
            if request.rating > 0:
                res += f"<b>Поставлена оценка: </b> {request.rating}, {request.rating_comment}\n"
        return res
    class Meta:
        verbose_name_plural = 'Мероприятия' 
        verbose_name = 'Мероприятие' 
        ordering = ['date','time']

class EventRequests(models.Model):
    number = models.AutoField("Номер заявки", primary_key=True)
    event = models.ForeignKey('Events', on_delete=models.PROTECT, verbose_name="Мероприятие",null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь",null=False, blank=False)
    for_status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Для статуса",null=False, blank=False)
    price = models.DecimalField("Стоимость мероприятия", max_digits=11, decimal_places=2)
    payed = models.BooleanField("Оплачена", default=False)
    confirmed = models.BooleanField("Подтверждена", default=False)
    qr_code_sended = models.BooleanField("QR код подтверждения отослан", default=False)
    rating = models.IntegerField("Оценка мероприятия", default=0, null=True, blank=True)
    rating_comment = models.TextField("Комментарий к оценке", null=True, blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    payment = models.ForeignKey(Payments, on_delete=models.PROTECT, verbose_name="Документ платежа",null=True, blank=True)
    def __str__(self):
        return f"{self.number} на {self.event} от пользователя {self.user} цена {self.price} руб."
    def get_qr_code(self):
        text = ""
        text += f"<b>{self.event}</b>\n"
        text += f"<b>Ф.И.О. гостя:</b>\n{self.user.last_name} {self.user.first_name} {self.user.sur_name}\n"
        text += f"<b>Статус:</b> {self.for_status}\n"
        text += f"<b>Организация:</b> {self.user.company}\n"
        text += f"<b>Должность:</b> {self.user.job}\n"
        qr_txt = text.replace("<b>", "").replace("</b>", "")
        img = qrcode.make(qr_txt)
        return img, text

    def description(self) -> str:
        text = "Заявка "
        date = self.created_at.strftime("%d.%m.%Y")
        text += f"<b>№{self.number}</b> от <b>{date}</b>\n"
        text += f"<b>На событие:</b> {self.event}\n"
        text += f"<b>От:</b> {self.user}\n"
        text += f"<b>Цена:</b> {self.price}\n"
        text += "<b>Оплачена</b>\n" if self.payed else "<b>Не оплачена</b>\n"
        text += "<b>Подтверждена</b>\n" if self.confirmed else "<b>Не подтверждена</b>\n"
        return text
    
    class Meta:
        verbose_name_plural = 'Заявки на мероприятия' 
        verbose_name = 'Заявка на мероприятие' 
        ordering = ['event','user']

class Anonses(models.Model):
    event = models.ForeignKey('Events', on_delete=models.PROTECT, verbose_name="Мероприятие",null=False, blank=False)
    text = models.TextField("Текст анонса", null=True, blank=True)
    sending_groups = models.ManyToManyField(tgGroups, verbose_name="Группы для рассылки")
    file = models.FileField("Фото/Видео", blank=True, null=True, upload_to="events")
    file_id = models.CharField("file_id", unique=False, max_length=255, blank=True, null = True)
    def __str__(self):
        res = f"{self.event} в "       
        res += ", ".join([group.name for group in self.sending_groups.all()])
        return res
    def show_groups(self)->str:
        res = ", ".join([group.name for group in self.sending_groups.all()])
        return res    
    show_groups.short_description = 'Отсылается в группы'
    class Meta:
        verbose_name_plural = 'Анонсы мероприятий' 
        verbose_name = 'Анонс мероприятия' 
        ordering = ["event"]

class AnonsesDates(models.Model):
    anons = models.ForeignKey(Anonses, on_delete=models.CASCADE, verbose_name="Анонс",null=False, blank=False)
    anons_date = models.DateField("Дата отправки", blank=False, null=False)
    sended = models.BooleanField("Отослан", default=False)
    class Meta:
        verbose_name_plural = 'Даты отправки анонсов' 
        verbose_name = 'Дата отправки анонса' 
        ordering = ["anons", "anons_date"]