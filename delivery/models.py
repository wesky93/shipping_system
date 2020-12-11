from django.db import models

# Create your models here.
from base.models import Region, User


class Deliverer(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    available_region = models.ManyToManyField(Region)
