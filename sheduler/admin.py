from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    readonly_fields = ["code"]
    list_display = ("name","time","interval","day") 
    list_display_links = ("name",) 
    search_fields = ("name",)
    fields = [('name'), 
              ('date', 'time'),    
              ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'san'), 
              ('day'),
              ('interval'),
              ('is_active'),
            ]

@admin.register(MessagesToSend)
class MessagesToSendAdmin(admin.ModelAdmin) :
    list_display = ("receiver","text", "created_at", "sended_at") 
    list_display_links = ("receiver","text" ) 
    search_fields = ("receiver",)
    readonly_fields = ["file_id","reply_markup"] 

@admin.register(MessageTemplates)
class MessageTemplatesAdmin(admin.ModelAdmin) :
    readonly_fields = ["code","file_id"]
    list_display = ("code","name") 
    list_display_links = ("code","name" ) 
    search_fields = ("code","name")