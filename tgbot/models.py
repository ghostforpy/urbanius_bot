# -*- coding: utf-8 -*-

import requests

from datetime import timedelta
from typing import Dict, List, Optional, Tuple

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from tgbot import utils


class Config(models.Model):
    """Модель настроек бота."""

    param_name = models.CharField(_('Наименование параметра'), max_length=255)
    param_val = models.TextField(_('Значение параметра'), null=True, blank=True)

    def __str__(self):
        return self.param_name

    class Meta:
        ordering = ['param_name']
        verbose_name = 'Параметр бота'
        verbose_name_plural = 'Параметры бота'

    @classmethod
    def load_config(cls) -> Dict[str, str]:
        config_params = cls.objects.all()
        result = {}
        for config_param in config_params:
            result[config_param.param_name] = config_param.param_val

        return result


class Sport(models.Model):
    name = models.CharField("Вид спорта",unique=True, max_length=150, blank=False)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Виды спорта' 
        verbose_name = 'Вид спорта' 
        ordering = ['name']

class UserSport(models.Model):
    sport = models.ForeignKey(Sport,on_delete=models.CASCADE, verbose_name="Вид спорта")
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return str(self.sport)
    class Meta:
        verbose_name_plural = 'Спорт' 
        verbose_name = 'Спорт' 
        ordering = ['user', 'sport']  

class Hobby(models.Model):
    name = models.CharField("Вид хобби",unique=True, max_length=150, blank=False)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Виды хобби' 
        verbose_name = 'Вид хобби' 
        ordering = ['name']

class UserHobby(models.Model):
    hobby = models.ForeignKey(Hobby,on_delete=models.CASCADE, verbose_name="Хобби")
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return str(self.hobby)
    class Meta:
        verbose_name_plural = 'Хобби пользователя' 
        verbose_name = 'Хобби пользователя' 
        ordering = ['user', 'hobby']        

class JobRegions(models.Model):
    name = models.CharField("Название региона работы",unique=True, max_length=150, blank=False)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Регионы работы' 
        verbose_name = 'Регион работы' 
        ordering = ['name']

class Needs(models.Model):
    name = models.CharField("Потребности",unique=True, max_length=150, blank=False)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Потребности' 
        verbose_name = 'Потребность' 
        ordering = ['name']

class UserNeeds(models.Model):
    need = models.ForeignKey(Needs,on_delete=models.CASCADE, verbose_name="Потребность")
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return str(self.need)
    class Meta:
        verbose_name_plural = 'Потребности пользователя' 
        verbose_name = 'Потребность пользователя' 
        ordering = ['user', 'need']


class Branch(models.Model):
    name = models.CharField("Отрасль",unique=True, max_length=150, blank=False)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Отрасли' 
        verbose_name = 'Отрасль' 
        ordering = ['name']

class Offers(models.Model):
    offer = models.TextField("Суть предложения", blank=False)
    image = models.FileField("Файл", blank=True, upload_to="offers")
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return  self.offer
    class Meta:
        verbose_name_plural = 'Предложения' 
        verbose_name = 'Предложение' 
        ordering = ['user']

class SocialNets(models.Model):
    name = models.CharField("Название сети", max_length=50, blank=False)
    link = models.URLField("Ссылка", blank=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return ": ".join([str(self.name), str(self.link)])
    class Meta:
        verbose_name_plural = 'Соц. сети' 
        verbose_name = 'Соц. сеть'
        ordering = ['user']

class Status(models.Model):
    stat_id = models.IntegerField("ИД статуса", null=True)
    name = models.CharField("Статус пользователя", unique=True, max_length=150, blank=False)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Статусы пользователя' 
        verbose_name = 'Статус пользователя' 
        ordering = ['name']

class tgGroups(models.Model):
    name = models.CharField("Группа пользователей",unique=True, max_length=150, blank=False)
    chat_id = models.BigIntegerField("ИД чата в Телеграм", null=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Группы пользователей' 
        verbose_name = 'Группа пользователей'
        ordering = ['name']

class UsertgGroups(models.Model):
    group = models.ForeignKey(tgGroups,on_delete=models.CASCADE, verbose_name="Группа")
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return str(self.need)
    class Meta:
        verbose_name_plural = 'Группы пользователя' 
        verbose_name = 'Группа пользователя' 
        ordering = ['user', 'group']



class UserReferrers(models.Model):
    referrer = models.ForeignKey("User",on_delete=models.CASCADE, related_name="referrer", verbose_name="Рекомендатель")
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user", verbose_name="Пользователь")
    def __str__(self):
        return str(self.referrer)
    class Meta:
        verbose_name_plural = 'Рекомендатели' 
        verbose_name = 'Рекомендатель' 
        ordering = ['user', 'referrer'] 

class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    username = models.CharField("Телеграм логин",max_length=32, null=True, blank=True)
    last_name = models.CharField("Фамилия", max_length=256, null=True, blank=True)
    first_name = models.CharField("Имя", max_length=256)
    sur_name = models.CharField("Отчество", max_length=150, null=True, blank=True)
    date_of_birth = models.DateField("Дата рождения", null=True, default=timezone.now)    
    language_code = models.CharField(max_length=8, null=True, blank=True, help_text="Telegram client's lang")
    deep_link = models.CharField("Ссылка", max_length=64, null=True, blank=True)

    is_blocked_bot = models.BooleanField("Заблоктрован", default=False)
    is_banned = models.BooleanField("Забанен", default=False)

    is_admin = models.BooleanField("Администратор",default=False)
    is_moderator = models.BooleanField("Модератор",default=False)

    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Изменен", auto_now=True)

    main_photo = models.ImageField("Основное фото", upload_to='user_fotos', null=True, blank=True)
    telefon = models.CharField("Телефон", max_length=13, null=True, blank=True)
    email = models.EmailField("E-mail", max_length=100, null=True, blank=True)
 
    citi = models.CharField("Город", max_length=150, null=True, blank=True)
    company = models.CharField("Компания", max_length=150, null=True, blank=True)
    job = models.CharField("Должность", max_length=150, null=True, blank=True)
    site = models.CharField("Сайт", max_length=150, null=True, blank=True)
    tags = models.CharField("Тэги", max_length=150, null=True, blank=True)
    about = models.TextField("О себе", null=True, blank=True)
    comment = models.TextField("комментарий", null=True, blank=True)
    # Ссылочные поля
    job_region = models.ForeignKey(JobRegions, on_delete=models.DO_NOTHING, verbose_name="Регион работы",null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, verbose_name="Отрасль",null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, verbose_name="Статус",null=True, blank=True)
    club_groups = models.ForeignKey(tgGroups, on_delete=models.DO_NOTHING, verbose_name="Клубная группа",null=True, blank=True)
    
    def __str__(self):
        res = f'@{self.username}' if self.username is not None else f'{self.user_id}'
        res = " ".join([res, str(self.first_name), str(self.last_name)])
        return res

    # Here I return the avatar or picture with an owl, if the avatar is not selected
    def get_avatar(self):
        if not self.main_photo:
            return '/media/no_foto.jpg'
        return self.main_photo.url
 
    # method to create a fake table field in read only mode width="100" 
    def avatar_tag(self):
        return mark_safe('<img src="%s" height="150" />' % self.get_avatar())
 
    avatar_tag.short_description = 'Avatar'

    @classmethod
    def get_user_and_created(cls, update, context) -> Tuple["User", bool]:
        """ python-telegram-bot's Update, Context --> User instance """
        data = utils.extract_user_data_from_update(update)
        u, created = cls.objects.update_or_create(user_id=data["user_id"], defaults=data)
 
        if created:
            u.is_blocked_bot = True
            u.comment = "Новый пользователь"
            if context is not None and context.args is not None and len(context.args) > 0:
                payload = context.args[0]
                if str(payload).strip() != str(data["user_id"]).strip():  # you can't invite yourself
                    u.deep_link = payload
                    u.save()
                    reffer = cls. get_user_by_username_or_user_id(str(payload).strip()) # Ищем рекомендателя и приписываем его пользователю
                    if reffer != None:
                        ur = UserReferrers(reffer, u)
                        ur.save()

        return u, created

    @classmethod
    def get_user(cls, update, context):
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(cls, string):
        """ Search user in DB, return User or None if not found """
        username = str(string).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    def invited_users(self):  # --> User queryset 
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    class Meta:
        verbose_name = 'Член клуба'
        verbose_name_plural = 'Члены клуба'


class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user: {self.user}, created at {self.created_at.strftime('(%H:%M, %d %B %Y)')}"

    def save(self, *args, **kwargs):
        super(Location, self).save(*args, **kwargs)
        # Parse location with arcgis
        #from .tasks import save_data_from_arcgis
        #save_data_from_arcgis.delay(latitude=self.latitude, longitude=self.longitude, location_id=self.pk)


class Arcgis(models.Model):
    location = models.OneToOneField(Location, on_delete=models.CASCADE, primary_key=True)

    match_addr = models.CharField(max_length=200)
    long_label = models.CharField(max_length=200)
    short_label = models.CharField(max_length=128)

    addr_type = models.CharField(max_length=128)
    location_type = models.CharField(max_length=64)
    place_name = models.CharField(max_length=128)

    add_num = models.CharField(max_length=50)
    address = models.CharField(max_length=128)
    block = models.CharField(max_length=128)
    sector = models.CharField(max_length=128)
    neighborhood = models.CharField(max_length=128)
    district = models.CharField(max_length=128)
    city = models.CharField(max_length=64)
    metro_area = models.CharField(max_length=64)
    subregion = models.CharField(max_length=64)
    region = models.CharField(max_length=128)
    territory = models.CharField(max_length=128)
    postal = models.CharField(max_length=128)
    postal_ext = models.CharField(max_length=128)

    country_code = models.CharField(max_length=32)

    lng = models.DecimalField(max_digits=21, decimal_places=18)
    lat = models.DecimalField(max_digits=21, decimal_places=18)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location}, city: {self.city}, country_code: {self.country_code}"

    @classmethod
    def from_json(cls, j, location_id):
        a = j.get("address")
        l = j.get("location")

        if "address" not in j or "location" not in j:
            return

        arcgis_data = {
            "match_addr": a.get("Match_addr"),
            "long_label": a.get("LongLabel"),
            "short_label": a.get("ShortLabel"),
            "addr_type": a.get("Addr_type"),
            "location_type": a.get("Type"),
            "place_name": a.get("PlaceName"),
            "add_num": a.get("AddNum"),
            "address": a.get("Address"),
            "block": a.get("Block"),
            "sector": a.get("Sector"),
            "neighborhood": a.get("Neighborhood"),
            "district": a.get("District"),
            "city": a.get("City"),
            "metro_area": a.get("MetroArea"),
            "subregion": a.get("Subregion"),
            "region": a.get("Region"),
            "territory": a.get("Territory"),
            "postal": a.get("Postal"),
            "postal_ext": a.get("PostalExt"),
            "country_code": a.get("CountryCode"),
            "lng": l.get("x"),
            "lat": l.get("y")
        }

        arc, _ = cls.objects.update_or_create(location_id=location_id, defaults=arcgis_data)
        return

    @staticmethod
    def reverse_geocode(lat, lng):
        r = requests.post(
            "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode",
            params={
                'f': 'json',
                'location': f'{lng}, {lat}',
                'distance': 50000,
                'outSR': '',
            },
            headers={
                'Content-Type': 'application/json',
            }
        )
        return r.json()


class UserActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=128)
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user: {self.user}, made: {self.action}, created at {self.created_at.strftime('(%H:%M, %d %B %Y)')}"
