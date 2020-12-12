from django.db import models
from django.db.models import OuterRef, QuerySet, Subquery, Sum
from django.db.models.functions import Coalesce


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class MenuQuerySetMixin():
    def get_queryset(self) -> QuerySet:
        return self

    def annotate_left_stock(self, date):
        from inventory.models import Stock
        left_stock_qs = Stock.objects.filter(date=date, menu=OuterRef('id')).annotate_left_stock().values_list(
            'left_stock')
        return self.get_queryset().annotate(left_stock=Sum(Subquery(left_stock_qs)))


class MenuQuerySet(QuerySet, MenuQuerySetMixin):
    pass


class MenuManager(models.Manager, MenuQuerySetMixin):
    def get_queryset(self):
        return MenuQuerySet(self.model, using=self._db)


# Create your models here.
class Menu(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    calorie = models.IntegerField(default=0)

    objects = MenuManager()

    def __str__(self):
        return f'{self.name}[{self.category.name}]({self.calorie})'


class SetMenuQuerySetMixin():
    def get_queryset(self) -> QuerySet:
        return self

    def total_calorie(self):
        return self.get_queryset().annotate(total_calorie=Sum('menus__calorie'))

    def annotate_left_stock(self, date):
        from inventory.models import Stock
        left_stock_qs = Menu.objects.filter(setmenu=OuterRef('id')).annotate_left_stock(date).order_by('left_stock')
        return self.get_queryset().annotate(left_stock=Coalesce(Subquery(left_stock_qs.values('left_stock')[:1]), 0))

    
class SetMenuQuerySet(QuerySet, SetMenuQuerySetMixin):
    pass


class SetMenuManager(models.Manager, SetMenuQuerySetMixin):
    def get_queryset(self):
        return SetMenuQuerySet(self.model, using=self._db)


class SetMenu(models.Model):
    name = models.CharField(max_length=200)
    menus = models.ManyToManyField(Menu)
    objects = SetMenuManager()

    def get_total_calorie(self):
        return self.menus.aggregate(Sum('calorie')).get('calorie__sum', 0)

    def get_left_stock(self, date):
        if hasattr(self,'left_stock'):
            return self.left_stock
        left_stock_qs = Menu.objects.filter(setmenu=self).annotate_left_stock(date).order_by('left_stock')
        return left_stock_qs.first().left_stock
    


    def __str__(self):
        return self.name


class Curation(models.Model):
    name = models.CharField(max_length=200)
    set_menus = models.ManyToManyField(SetMenu, through='CurationPriority')

    def __str__(self):
        return self.name

    def get_available_set_menu(self, date):
        result = self.set_menus.annotate_left_stock(date).values()
        set_menu_left_stock = {obj['id']: obj['left_stock'] for obj in result}
        for obj in CurationPriority.objects.filter(curation=self).order_by('priority').select_related('set_menu').all():
            if set_menu_left_stock[obj.set_menu.id]:
                return obj.set_menu
        return None


class CurationPriority(models.Model):
    class Meta:
        ordering = ("priority",)

    curation = models.ForeignKey(Curation, on_delete=models.CASCADE)
    set_menu = models.ForeignKey(SetMenu, on_delete=models.PROTECT)
    priority = models.PositiveIntegerField(default=0)
