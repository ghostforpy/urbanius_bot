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
