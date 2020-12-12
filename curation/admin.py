from admin_numeric_filter.admin import NumericFilterModelAdmin, SliderNumericFilter
from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin

# Register your models here.
from curation.models import Category, Curation, Menu, SetMenu


class CategoryMenuTabularInline(admin.TabularInline):
    model = Menu


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category
    search_fields = ('name',)

    inlines = (CategoryMenuTabularInline,)


@admin.register(Menu)
class MenuAdmin(NumericFilterModelAdmin):
    model = Menu
    search_fields = ('name', 'category__name',)
    list_display = ('name', 'category', 'calorie',)
    list_filter = ('category', ('calorie', SliderNumericFilter))


class MenuTabularInline(admin.TabularInline):
    model = SetMenu.menus.through
    autocomplete_fields = ('menu',)

    readonly_fields = ('category', 'calorie',)

    def category(self, instance):
        return instance.menu.category if instance.menu else ''

    category.short_description = '카테고리'

    def calorie(self, instance):
        return instance.menu.calorie if instance.menu else ''

    calorie.short_description = "칼로리"


@admin.register(SetMenu)
class SetMenuAdmin(admin.ModelAdmin):
    model = SetMenu
    list_display = ('name', 'total_calorie',)

    search_fields = ('name', 'menus__menu__name')

    fieldsets = [
        (None, {'fields': ['name']}),
        ('기본 정보', {'fields': ['total_calorie']})
    ]

    inlines = (MenuTabularInline,)

    def get_queryset(self, request):
        return super(SetMenuAdmin, self).get_queryset(request).total_calorie()

    readonly_fields = ('total_calorie',)

    def total_calorie(self, instance):
        return instance.total_calorie if hasattr(instance, 'total_calorie') else instance.get_total_calorie()

    # short_description functions like a model field's verbose_name
    total_calorie.short_description = "총 칼로리"


class CurationPriorityTabularInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Curation.set_menus.through
    verbose_name = '세트 메뉴'


@admin.register(Curation)
class CurationAdmin(admin.ModelAdmin):
    model = Curation
    search_fields = ('name', 'set_menus__set_menu__name')

    inlines = (CurationPriorityTabularInline,)
