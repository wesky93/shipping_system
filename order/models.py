from django.conf import settings
from django.db import models

from base.models import Region
from inventory.models import Provider, Stock


class OrderState(models.TextChoices):
    NEW = 'NEW', '신규주문'
    FOOD_ASSIGNMENT = 'FOOD_ASSIGNMENT', '음식배정'
    READY = 'READY', '배송준비'
    DELIVERING = 'DELIVERING', '배송중'
    DELIVERED = 'DELIVERED', '배송완료'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=100, choices=OrderState.choices, default=OrderState.NEW.value)
    date = models.DateField()
    new_address = models.TextField()
    old_address = models.TextField()
    etc_address = models.TextField(default='')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    zip = models.CharField(max_length=5)
    stocks = models.ManyToManyField(Stock)

    def __str__(self):
        return f"{self.__class__.__name__}({self.pk})<{self.date}|{self.user}>"

