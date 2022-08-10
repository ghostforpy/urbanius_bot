from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(TaskTypes)
class TaskTypesAdmin(admin.ModelAdmin) :
    list_display = ("name",) 
    list_display_links = ("name", ) 
    search_fields = ("name",)

@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin) :
    list_display = ("name","task_type","time") 
    list_display_links = ("name", "task_type") 
    search_fields = ("name",)
    fields = [('name', 'task_type'), 
              ('date', 'time'),    
              ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'san'), 
              ('day'),
              ('interval'),
              ('is_active'),
            ]
    # actions = ['restart_tasks']
    # @admin.action(description='Перезапустить задачи')
    # def restart_tasks(self, request, queryset):
    #     """ Select tasks via check mark in django-admin panel, then select "Broadcast" to send message"""
    #     restarts_tasks(my_app.dispatcher.job_queue)