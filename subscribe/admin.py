from django.contrib import admin
from .models import *

class PackageDescrForStatusInline(admin.TabularInline):
    model = PackageDescrForStatus

class PackagePricesInline(admin.TabularInline):
    model = PackagePrices


@admin.register(ClubPackages)
class ClubPackagesAdmin(admin.ModelAdmin) :
    list_display = ("code","name") 
    list_display_links = ("code","name") 
    search_fields = ("name",)
    readonly_fields = ["code"]
    inlines = [PackageDescrForStatusInline, PackagePricesInline]

@admin.register(PackageRequests)
class PackageRequestsAdmin(admin.ModelAdmin) :
    list_display = ("number","created_at", "package", "user", "price" , "date_from", "date_to", "payed", "confirmed") 
    list_display_links = ("number","created_at", "package", "user") 
    search_fields = ("package", "user",)
    readonly_fields = ["number","created_at"]
    list_filter = ["payed", "confirmed"] 