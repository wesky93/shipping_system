from django.db import models
from django.db.models import QuerySet, Sum


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Create your models here.
class Menu(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    calorie = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.name}[{self.category.name}]({self.calorie})'


# todo: 세트메뉴 총 칼로리 annotation 추가한 쿼리셋 추가

class SetMenuQuerySetMixin():
    def get_queryset(self):
        return self

    def total_calorie(self):
        return self.get_queryset().annotate(total_calorie=Sum('menus__calorie'))


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

    def __str__(self):
        return self.name


class Curation(models.Model):
    name = models.CharField(max_length=200)
    set_menus = models.ManyToManyField(SetMenu, through='CurationPriority')

    def __str__(self):
        return self.name


class CurationPriority(models.Model):
    class Meta:
        ordering = ("priority",)

    curation = models.ForeignKey(Curation, on_delete=models.CASCADE)
    set_menu = models.ForeignKey(SetMenu, on_delete=models.PROTECT)
    priority = models.PositiveIntegerField(default=0)
