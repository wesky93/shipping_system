from django.db import models


# Create your models here.
class Menu(models.Model):
    name = models.CharField(max_length=200)
    calorie = models.IntegerField()

    def __unicode__(self):
        return self.name


class SetMenu(models.Model):
    name = models.CharField(max_length=200)
    menus = models.ManyToManyField(Menu)

    def __unicode__(self):
        return self.name


class Curation(models.Model):
    name = models.CharField(max_length=200)
    set_menus = models.ManyToManyField(SetMenu, through='CurationPriority')

    def __unicode__(self):
        return self.name


class CurationPriority(models.Model):
    class Meta:
        ordering = ("priority",)

    curation = models.ForeignKey(Curation, on_delete=models.CASCADE)
    set_menu = models.ForeignKey(SetMenu, on_delete=models.CASCADE)
    priority = models.PositiveIntegerField(default=0)
