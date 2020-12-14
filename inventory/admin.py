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
    list_display = ('date', 'provider', 'menu', 'count', 'left_stock')
    list_select_related = ('provider', 'menu',)
    list_filter = ('provider__name', 'date',)
    autocomplete_fields = ('provider', 'menu',)
    search_fields = ('menu__name', 'provider__name')

    def get_queryset(self,request):
        return super(StockAdmin, self).get_queryset(request).annotate_left_stock()

    readonly_fields = ('left_stock',)

    def left_stock(self, instance):
        return instance.left_stock if hasattr(instance, 'left_stock') else instance.get_left_stock()

    # short_description functions like a model field's verbose_name
    left_stock.short_description = "남은 재고"
