from django.contrib import admin
from .models import *

@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin) :
    list_display = ("created_at","user","price") 
    list_display_links = ("created_at","user","price") 
    search_fields = ("user",)