from django.contrib import admin

from .models import Provider, Stock


class StockTabularInline(admin.TabularInline):
    model = Stock
    autocomplete_fields = ('menu',)


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    model = Provider
    list_display = ('name',)

    search_fields = ('name',)

    fieldsets = [
        (None, {'fields': ['name']}),
    ]

    inlines = (StockTabularInline,)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    model = Stock
    list_display = ('date', 'provider', 'menu', 'count',)
    list_select_related = ('provider', 'menu',)
    list_filter = ('provider__name', 'date',)
    autocomplete_fields = ('provider', 'menu',)
    search_fields = ('menu__name', 'provider__name')
