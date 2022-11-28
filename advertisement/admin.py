from django.contrib import admin
from .models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ("author", "admin_aprooved", "created_at",) 
    search_fields = ("author", "essence",)
    list_filter = ["admin_aprooved", "created_at",] 
    readonly_fields = ["file_id", "created_at",]
    fields = [
        "author",
        "essence",
        "file",
        "file_id",
        "admin_aprooved", 
        "created_at",
    ]

