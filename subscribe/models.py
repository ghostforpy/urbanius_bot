import datetime
from django.db import models
from tgbot.models import User, tgGroups, Status
from payments.models import Payments

class ClubPackages(models.Model):
    code = models.CharField("Код пакета", unique=True, max_length=30, blank=False)
    name = models.CharField("Пакет участия", max_length=150, blank=False)
    def __str__(self):
        return self.name

    def get_subscrition_txt(self, user: User) -> str:
        #
        reqw = self.packagerequests_set.filter(user = user, date_to__gte = datetime.date.today())
        if reqw:
            rewqest =  reqw.latest('date_to')
            return f"Подписка действует до {rewqest.date_to}"
        else:
            return "Отсутствует действующая подписка"

    class Meta:
        verbose_name_plural = 'Пакеты участия' 
        verbose_name = 'Пакет участия' 
        ordering = ['name',]

class PackageDescrForStatus(models.Model):
    package =  models.ForeignKey(ClubPackages, on_delete=models.CASCADE, verbose_name="Пакет")
    for_status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Для статуса",null=False, blank=False)
    description = models.TextField("Описание", null=True, blank=True)
    def __str__(self):
        return f"Описание пакета {self.package} для статуса {self.for_status}"
    class Meta:
        verbose_name_plural = 'Описание пакетов участия' 
        verbose_name = 'Описание пакета участия' 
        ordering = ['package','for_status']

class PackagePrices(models.Model):
    package = models.ForeignKey(ClubPackages, on_delete=models.CASCADE, verbose_name="Пакет", null=False, blank=False)
    for_status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Для статуса",null=False, blank=False)
    price = models.DecimalField("Стоимость", max_digits=11, decimal_places=2)
    period = models.IntegerField("Период, мес.", null=False, blank=False)
    def __str__(self):
        return f"{self.package} для статуса {self.for_status} цена {self.price} руб. на {self.price} мес." 
    class Meta:
        verbose_name_plural = 'Стоимость пакетов' 
        verbose_name = 'Стоимость пакета' 
        ordering = ['package']

class PackageRequests(models.Model):
    number = models.AutoField("Номер заявки", primary_key=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    package = models.ForeignKey(ClubPackages, on_delete=models.PROTECT, verbose_name="Пакет участия",null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь",null=False, blank=False)
    for_status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Для статуса",null=False, blank=False)
    package_price = models.ForeignKey(PackagePrices, on_delete=models.PROTECT, verbose_name="Цена пакета",null=False, blank=False)
    price = models.DecimalField("Стоимость пакета", max_digits=11, decimal_places=2)
    date_from = models.DateField("Период с", null=False, blank=False)
    date_to = models.DateField("Период по", null=False, blank=False)
    payed = models.BooleanField("Оплачена", default=False)
    confirmed = models.BooleanField("Подтверждена", default=False)
    payment = models.ForeignKey(Payments, on_delete=models.PROTECT, verbose_name="Документ платежа",null=True, blank=True)
    def __str__(self):
        return f"{self.number} на {self.package} от пользователя {self.user} цена {self.price} руб."

    def getdescr(self)->str:
        payed = "Оплачена" if self.payed else "Не оплачена"
        confirmed = "Подтверждена"  if self.confirmed else "Не подтверждена"
        return f"№{self.number} от {self.created_at} цена {self.price} руб. на период с {self.date_from} по {self.date_to}, {payed}, {confirmed}"
    class Meta:
        verbose_name_plural = 'Заявки на пакет участия' 
        verbose_name = 'Заявка на пакет участия' 
        ordering = ['created_at','package','user']