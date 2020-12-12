from typing import Union

from django.conf import settings
from django.db import models
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by

from base.models import Region
from curation.models import Curation, SetMenu
from delivery.models import Deliverer
from inventory.models import Provider, Stock


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

        self.stocks.set(Stock.objects.available(self.date).filter(menu__in=set_menu.menus.all()).distinct('menu'))
        self.save()

    @fsm_log_by
    @transition(field=state, source=OrderState.FOOD_ASSIGNMENT.value, target=OrderState.READY.value, )
    def deliverer_assignment(self):
        pass

    @fsm_log_by
    @transition(field=state, source=OrderState.READY.value, target=OrderState.DELIVERING.value, )
    def departure(self):
        pass

    @fsm_log_by
    @transition(field=state, source=OrderState.DELIVERING.value, target=OrderState.DELIVERED.value, )
    def finish(self):
        pass
