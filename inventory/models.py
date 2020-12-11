from django.db import models

from curation.models import Menu


class Provider(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Stock(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.PROTECT)
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT)
    date = models.DateField()
    count = models.PositiveIntegerField(default=0)
