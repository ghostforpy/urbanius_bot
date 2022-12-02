from django.contrib import admin
from .models import Advertisement, AdvertisementVideo, AdvertisementImage


class AdvertisementVideoInline(admin.TabularInline):
    model = AdvertisementVideo


class AdvertisementImageInline(admin.TabularInline):
    model = AdvertisementImage


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ("author", "admin_aprooved", "created_at",) 
    search_fields = ("author", "essence",)
    list_filter = ["admin_aprooved", "created_at",] 
    readonly_fields = ["created_at",]
    fields = [
        "author",
        "essence",
        "admin_aprooved", 
        "created_at",
    ]
    inlines = [AdvertisementImageInline, AdvertisementVideoInline]


@admin.register(AdvertisementVideo)
class AdvertisementVideoAdmin(admin.ModelAdmin):
    pass


@admin.register(AdvertisementImage)
class AdvertisementImageAdmin(admin.ModelAdmin):
    pass