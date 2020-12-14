from typing import Union

from django.conf import settings
from django.db import models
from django.db.models import Count, OuterRef, Subquery, Sum
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by

from base.models import Region
from curation.models import Curation, SetMenu
from delivery.models import Deliverer
from inventory.models import Stock


class OrderState(models.TextChoices):
    NEW = 'NEW', '신규주문'
    FOOD_ASSIGNMENT = 'FOOD_ASSIGNMENT', '음식배정'
    READY = 'READY', '배송준비'
    DELIVERING = 'DELIVERING', '배송중'
    DELIVERED = 'DELIVERED', '배송완료'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    state = FSMField(default=OrderState.NEW.value, choices=OrderState.choices, protected=True)

    date = models.DateField()
    new_address = models.TextField()
    old_address = models.TextField()
    etc_address = models.TextField(default='')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    zip = models.CharField(max_length=5)
    deliverer = models.ForeignKey(Deliverer, on_delete=models.SET_NULL, null=True)
    stocks = models.ManyToManyField(Stock)

    def __str__(self):
        return f"{self.__class__.__name__}({self.pk})<{self.date}|{self.user}>"

    @fsm_log_by
    @transition(field=state, source=OrderState.NEW.value, target=OrderState.FOOD_ASSIGNMENT.value, )
    def curation(self, set_menu_or_curation: Union[SetMenu, Curation, None] = None, **kwargs):
        from inventory.models import Stock

        if isinstance(set_menu_or_curation, SetMenu):
            set_menu = set_menu_or_curation
        else:
            if set_menu_or_curation is None:  # from admin
                curation_obj = Curation.objects.get(id=kwargs.get('request').POST.get('curation_menu'))
            else:
                curation_obj = set_menu_or_curation
            set_menu = curation_obj.get_available_set_menu(self.date)
            if not set_menu:
                raise ValueError('No Stock')

        if not set_menu.get_left_stock(self.date):
            raise ValueError('No Stock')

        left_stock_qs = Stock.objects \
            .filter(date=self.date, menu=OuterRef('id')) \
            .annotate_left_stock() \
            .order_by('left_stock').values_list('id', flat=True)

        stocks = set_menu.menus.annotate(stock_id=Subquery(left_stock_qs[:1])).values_list('stock_id', flat=True)

        self.stocks.set(stocks)

    @fsm_log_by
    @transition(field=state, source=OrderState.FOOD_ASSIGNMENT.value, target=OrderState.READY.value, )
    def deliverer_assignment(self, **kwargs):
        subquery = Order.objects.filter(date=self.date, deliverer=OuterRef('pk')).only('pk')
        deliverer = Deliverer.objects \
            .filter(available_region__in=[self.region]) \
            .annotate(order_sum=Count(Subquery(subquery))) \
            .order_by('order_sum') \
            .first()

        if not deliverer:
            raise ValueError('No deliverer')
        self.deliverer = deliverer

    @fsm_log_by
    @transition(field=state, source=OrderState.READY.value, target=OrderState.DELIVERING.value, )
    def departure(self):
        pass

    @fsm_log_by
    @transition(field=state, source=OrderState.DELIVERING.value, target=OrderState.DELIVERED.value, )
    def finish(self):
        pass
