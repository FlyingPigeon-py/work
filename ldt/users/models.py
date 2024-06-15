import sys

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

if "makemigrations" not in sys.argv and "migrate" not in sys.argv:
    AbstractUser._meta.get_field("email")._unique = True


class CustomUserManager(BaseUserManager):
    def by_mail(self, email):
        return self.get_queryset().filter(email=email).first()

    def get_oders_count(self):
        pass

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    objects = CustomUserManager()

    email = models.EmailField(
        "Email",
        max_length=100,
        unique=True

    )

    username = models.CharField(
        "Имя пользователя",
        max_length=100,
        help_text="Введите имя",
        blank=True,
        null=True,
        editable=False
    )
    avatar = models.ImageField(
        upload_to='avatars',

    )
    birthday = models.DateField(
        "дата рождения",
        help_text="Введите дату рождения",
        blank=True,
        null=True,
    )

    middle_name = models.CharField(
        "отчество",
        max_length=100,
        help_text="Введите Отчество",
        blank=True,
        null=True,
    )

    first_name = models.CharField(
        "имя",
        max_length=150,
        help_text="Введите Имя",
    )

    last_name = models.CharField(
        "фамилия",
        max_length=150,
        help_text="Введите Фамилию",
    )

    def __str__(self):
        return self.get_name() + " (" + self.email + ")"

    def get_name(self):
        name = self.email
        if self.last_name:
            name = str(self.last_name + " ").capitalize()
        if self.first_name:
            name += str(self.first_name[0] + ". ").capitalize()
        if self.middle_name:
            name += str(self.middle_name[0] + ". ").capitalize()

        return name

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


__all__ = []
