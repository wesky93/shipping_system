from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        user = self.model(
            email=self.normalize_email(email),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    email = models.EmailField(unique=True, )
    name = models.CharField(max_length=150, )
    is_staff = models.BooleanField(
        _('is_staff'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', ]


class Region(models.Model):
    class Meta:
        index_together = [
            ["city", "district", 'town', ],
        ]
        unique_together = ('city', 'district', 'town',)

    city = models.CharField(max_length=50, help_text='시/도')
    district = models.CharField(max_length=50, help_text='시/구/군')
    town = models.CharField(max_length=50, help_text='읍/면/동')

    def __str__(self):
        return f"<{self.city}|{self.district}|{self.town}>"

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    old = models.TextField(blank=True, help_text='구주소')
    new = models.TextField(blank=True, help_text='신주소')
    zip = models.CharField(blank=True, help_text='우편번호', max_length=5)
    etc = models.TextField(blank=True, help_text='기타 주소', default='')
    region = models.ForeignKey(Region, on_delete=models.PROTECT, blank=True)
