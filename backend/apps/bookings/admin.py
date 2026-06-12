from django.contrib import admin

from .models import Booking, Traveler


class TravelerInline(admin.TabularInline):
    model = Traveler
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("contact_name", "route", "party_size", "travel_date", "status", "traveler_count")
    list_filter = ("status", "travel_date")
    search_fields = ("contact_name", "phone", "route__title")
    inlines = [TravelerInline]

    def traveler_count(self, obj):
        return obj.travelers.count()

    traveler_count.short_description = "游客数"


@admin.register(Traveler)
class TravelerAdmin(admin.ModelAdmin):
    list_display = ("name", "booking", "id_type", "id_number", "age")
    list_filter = ("id_type",)
    search_fields = ("name", "id_number", "booking__contact_name")
