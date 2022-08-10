# -*- coding: utf-8 -*-

import requests
import operator
from django.db.models import Q

from datetime import timedelta
from typing import Dict, List, Optional, Tuple

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from tgbot import utils

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
    code = models.IntegerField("Код региона",unique=False, null=True)
    name = models.CharField("Название региона работы",unique=True, max_length=150, blank=False)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Регионы работы' 
        verbose_name = 'Регион работы' 
        ordering = ['code']


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

class SocialNetSites(models.Model):
    name = models.CharField("Название сайта", max_length=50, blank=False)
    link = models.URLField("Ссылка", blank=False)
    def __str__(self):
        return str(self.name)
    class Meta:
        verbose_name_plural = 'Сайты соц. сетей' 
        verbose_name = 'Сайт соц. сети'
        ordering = ['name']

class SocialNets(models.Model):
    soc_net_site = models.ForeignKey(SocialNetSites, on_delete=models.CASCADE, verbose_name="Сайт соц. сети")
    link = models.URLField("Страница", blank=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return ": ".join([str(self.soc_net_site), str(self.link)])
    class Meta:
        verbose_name_plural = 'Страницы в соц. сети' 
        verbose_name = 'Страница в соц. сети'
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
    link = models.CharField("Ссылка на группу",unique=False, max_length=150, blank=True)
    def __str__(self):
        return self.name

    @classmethod
    def get_group_by_name(cls, gr_name: str) -> "tgGroups":
        return cls.objects.filter(name = gr_name).first()

    class Meta:
        verbose_name_plural = 'Группы пользователей' 
        verbose_name = 'Группа пользователей'
        ordering = ['name']

class UsertgGroups(models.Model):
    group = models.ForeignKey(tgGroups,on_delete=models.CASCADE, verbose_name="Группа")
    user = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return str(self.group)
    class Meta:
        verbose_name_plural = 'Группы пользователя' 
        verbose_name = 'Группа пользователя' 
        ordering = ['user', 'group']


class UserReferrers(models.Model):
    referrer = models.ForeignKey("User",on_delete=models.CASCADE, related_name="referrer", verbose_name="Рекомендатель")
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="userreferrers_set", verbose_name="Пользователь")
    def __str__(self):
        return str(self.referrer)
    class Meta:
        verbose_name_plural = 'Рекомендатели' 
        verbose_name = 'Рекомендатель' 
        ordering = ['user', 'referrer'] 

class User(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    username = models.CharField("Телеграм логин",max_length=32, null=True, blank=True)
    last_name = models.CharField("Фамилия", max_length=256, null=True, blank=True)
    first_name = models.CharField("Имя", max_length=256)
    sur_name = models.CharField("Отчество", max_length=150, null=True, blank=True)
    date_of_birth = models.DateField("Дата рождения", null=True, default=timezone.now)    
    language_code = models.CharField(max_length=8, null=True, blank=True, help_text="Telegram client's lang")
    deep_link = models.CharField("Ссылка", max_length=64, null=True, blank=True)

    is_blocked_bot = models.BooleanField("Заблокирован", default=False)
    is_banned = models.BooleanField("Забанен", default=False)

    is_admin = models.BooleanField("Администратор",default=False)
    is_moderator = models.BooleanField("Модератор",default=False)
    random_coffe_on = models.BooleanField("Подключено Random coffe",default=False)

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
    needs = models.TextField("Потребности", null=True, blank=True)
    about = models.TextField("О себе", null=True, blank=True)
    comment = models.TextField("комментарий", null=True, blank=True)
    # Ссылочные поля
    job_region = models.ForeignKey(JobRegions, on_delete=models.DO_NOTHING, verbose_name="Регион работы",null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, verbose_name="Отрасль",null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, verbose_name="Статус",null=True, blank=True)

    
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
    def get_user(cls, update, context) -> "User":
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(cls, string) -> "User":
        """ Search user in DB, return User or None if not found """
        username = str(string).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()


    @classmethod
    def find_users_by_keywords(cls, keywords) -> list:
        """ осуществляет поиск участников, у которых в любом поле упоминаются ключевые слова """
        q = Q(username__icontains = keywords)| \
            Q(last_name__icontains = keywords)| \
            Q(first_name__icontains = keywords)| \
            Q(sur_name__icontains = keywords)| \
            Q(deep_link__icontains = keywords)| \
            Q(telefon__icontains = keywords)| \
            Q(email__icontains = keywords)| \
            Q(citi__icontains = keywords)| \
            Q(company__icontains = keywords)| \
            Q(job__icontains = keywords)| \
            Q(site__icontains = keywords)| \
            Q(tags__icontains = keywords)| \
            Q(needs__icontains = keywords)| \
            Q(about__icontains = keywords)| \
            Q(comment__icontains = keywords)| \
            Q(job_region__name__icontains = keywords)| \
            Q(branch__name__icontains = keywords)| \
            Q(status__name__icontains = keywords)| \
            Q(usersport__sport__name__icontains = keywords)| \
            Q(userhobby__hobby__name__icontains = keywords)| \
            Q(offers__offer__icontains = keywords)| \
            Q(socialnets__link__icontains = keywords)| \
            Q(socialnets__soc_net_site__name__icontains = keywords)| \
            Q(usertggroups__group__name__icontains = keywords)|\
            Q(userreferrers_set__referrer__username__icontains = keywords)|\
            Q(userreferrers_set__referrer__last_name__icontains = keywords)
        users = cls.objects.filter(q).distinct()


        return users

    def short_profile(self)->str:
        res = "<b>Пользователь:</b> \n"
        res += str(self)
        res += "\n<b>Регион:</b> \n"
        res += utils.mystr(self.job_region)
        res += "\n<b>Отрасль:</b> \n"
        res += utils.mystr(self.branch)
        res += "\n<b>Компания:</b> \n"
        res += utils.mystr(self.company)
        res += "\n<b>Должность:</b> \n"
        res += utils.mystr(self.job)
        res += "\n<b>О себе:</b> \n"
        res += utils.mystr(self.about)
   
        return res

    def full_profile(self)->str:
        res = "<b>Пользователь:</b> \n"
        res += str(self)        
        res += "\n<b>Личная информация:</b> "
        res += "\n  <b>e-mail:</b> " + utils.mystr(self.email)
        res += "\n  <b>Телефон:</b> " + utils.mystr(self.telefon)
        res += "\n  <b>Дата рождения:</b> " + utils.mystr(self.date_of_birth)
        res += "\n  <b>Статус:</b> " + utils.mystr(self.status)
        res += "\n<b>Группы:</b>\n" + get_model_text(UsertgGroups,["NN","group"], self)

   
        return res
    def invited_users(self):  # --> User queryset 
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class MessagesToSend(models.Model):
    receiver  = models.ForeignKey("User", on_delete=models.CASCADE, related_name="receiver", verbose_name="Получатель", blank=False, null=False)    
    text = models.TextField("Текст сообщения",unique=False, blank=False)
    created_at = models.DateTimeField("Создано в", auto_now_add=True)
    sended_at = models.DateTimeField("Отослано в")
    sended = models.BooleanField("Отослано", default=False)
    recommended_friend = models.ForeignKey("User", on_delete=models.SET_NULL, related_name="recommended_friend", verbose_name="Рекомендованный друг по Random coffe", blank=True, null=True)
    file = models.FileField("Файл", blank=True, upload_to="messages")

    def __str__(self):
        return self.text
    class Meta:
        verbose_name_plural = 'Сообщения к отсылке' 
        verbose_name = 'Сообщение к отсылке' 
        ordering = ['created_at']


class UserActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=128)
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user: {self.user}, made: {self.action}, created at {self.created_at.strftime('(%H:%M, %d %B %Y)')}"

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

# Получает из всех записей модели словарь 
# key - имя поля чье значение попадет в ключ, 
# value имя поля чье значение попадет в значение если "NN" то подставится порядковый номер
# parent значение родительской модели для выборки подчиненных элементов 
def get_dict(model, key: str, value: str, parent = None, filter = None):
    res = dict()
    if parent:
        model_set = getattr(parent,model._meta.model_name+"_set") # получаем выборку дочерних записей parent
    else:
        model_set = model.objects # получаем выборку записей
    
    if filter:
        model_set = model_set.filter(**filter)
    else:
        model_set = model_set.all()
    fields = value.split(",")
    str_num = 0
    for elem in model_set:
        str_num += 1
        val_list = []
        for field in fields:
            if field == "NN":
                val_list.append(str(str_num))
            else:
                val_list.append(str(getattr(elem, field.strip())))
        res[str(getattr(elem, key))] = ", ".join(val_list)
    return res

# Получает из всех записей текст 
# fields - список полей которые попадут в текст "NN" - спец поле будет подставляться номер строки
# parent значение родительской модели для выборки подчиненных элементов 
def get_model_text(model, fields: list, parent = None, filter = None ):
    res = ""
    if parent:
        model_set = getattr(parent,model._meta.model_name+"_set") # получаем выборку дочерних записей parent
    else:
        model_set = model.objects # получаем выборку записей
    
    if filter:
        model_set = model_set.filter(**filter)
    else:
        model_set = model_set.all()
    
    str_num = 0
    for elem in model_set:
        str_num += 1
        txt_str_lst = []
        for field in fields:
            if field == "NN":
                txt_str_lst.append(str(str_num)) 
            else:
                txt_str_lst.append(str(getattr(elem, field)))
        txt_str = ", ".join(txt_str_lst)+"\n"
        res += txt_str

    return res



