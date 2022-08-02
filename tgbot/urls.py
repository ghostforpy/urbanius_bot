# -*- coding: utf-8 -*-

from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.contrib import admin
from . import views

urlpatterns = [  
    # TODO: make webhook more secure
    path('', views.index, name="index"),
    #path('', admin.site.urls),
    path('super_secter_webhook/', csrf_exempt(views.TelegramBotWebhookView.as_view())),
]
