from django.contrib import admin
from .models import *

@admin.register(Partnes)
class PartnesAdmin(admin.ModelAdmin):
    list_display = ("short_name","full_name","email") 
    list_display_links = ("short_name","full_name","email") 
    search_fields = ("short_name","full_name","email")

class SpecialOffersDatesInline(admin.TabularInline):
    model = SpecialOffersDates
class SpecialOffersDiscountsInline(admin.TabularInline):
    model = SpecialOffersDiscounts

@admin.register(SpecialOffers)
class SpecialOffersAdmin(admin.ModelAdmin):
    list_display = ("partner","user","name","valid_until","show_groups") 
    list_display_links = ("partner","user","name","valid_until","show_groups") 
    search_fields = ("offer",)
    filter_horizontal = ('sending_groups',)
    readonly_fields = ["file_id",]
    inlines = [SpecialOffersDatesInline, SpecialOffersDiscountsInline]

@admin.register(SOUserRequests)
class SOUserRequestsAdmin(admin.ModelAdmin):
    list_display = ("created_at","offer","user","discount") 
    list_display_links = ("created_at","offer","user","discount") 
    search_fields = ("offer","user",)