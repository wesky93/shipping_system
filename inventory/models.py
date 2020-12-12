from django.db import models
from django.db.models import Count, F, QuerySet

from curation.models import Menu


class Provider(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class StockQuerySetMixin():
    def get_queryset(self) -> QuerySet:
        return self

    def annotate_assignment(self):
        return self.get_queryset().annotate(assignment_stock=Count('order'))

    def annotate_left_stock(self):
        return self.get_queryset().annotate_assignment().annotate(left_stock=F('count') - F('assignment_stock'))

    def available(self, date):
        return self.get_queryset().filter(date=date).annotate_left_stock().filter(left_stock__gte=1)


class StockQuerySet(QuerySet, StockQuerySetMixin):
    pass


class StockManager(models.Manager, StockQuerySetMixin):
    def get_queryset(self):
        return StockQuerySet(self.model, using=self._db)


class Stock(models.Model):
    objects = StockManager()

    provider = models.ForeignKey(Provider, on_delete=models.PROTECT)
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT)
    date = models.DateField()
    count = models.PositiveIntegerField(default=0)
