from datetime import datetime
from django.utils import timezone

import phonenumbers
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderManager(models.Manager):

    def get_orders_count_for_employee(self, user):
        return self.filter(employee=user).count()

    def get_orders_done_count_for_employee(self, user):
        return self.filter(employee=user, status=True).count()

    def orders_without_employee(self):
        return self.filter(employee=None, status=False)

    def orders_with_employee_false_status(self):
        return self.filter(employee__isnull=False, status=False)

    def orders_with_status_true(self):
        return self.filter(status=True)

    def orders_with_employee_false_status_for_employee(self, employee_id):
        return self.filter(employee=employee_id, status=False)

    def orders_with_status_true_for_employee(self, employee_id):
        return self.filter(employee=employee_id, status=True)

    def orders_created_this_month(self):
        current_date = timezone.now()
        start_of_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.filter(creation_time__gte=start_of_month)

    def orders_created_today(self):
        current_date = timezone.now()
        start_of_day = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        return self.filter(creation_time__range=(start_of_day, end_of_day))


class Order(models.Model):
    objects = OrderManager()

    PAYMENT_CHOICES = [
        ('при_получении', _('При получении')),
        ('оплачено', _('Оплачено')),
    ]

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        verbose_name=_('Способ оплаты'),
        help_text=_('Выберите способ оплаты для этого заказа.')
    )
    creation_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания'),
        help_text=_('Дата и время создания этого заказа.')
    )
    delivery_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата доставки'),
        help_text=_('Планируемая дата доставки этого заказа.')
    )
    status = models.BooleanField(
        verbose_name=_('Статус'),
        help_text=_('Статус выполнения этого заказа.')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название'),
        help_text=_('Название этого заказа.')
    )
    client = models.CharField(
        max_length=150,
        verbose_name=_('Клиент'),
        help_text=_('Имя клиента, оформившего этот заказ.')
    )
    contact_number = models.CharField(
        max_length=25,
        verbose_name=_('Контактный номер'),
        help_text=_('Контактный номер клиента для связи.')
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='employee_user',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Исполнитель'),
        help_text=_('Пользователь, ответственный за выполнение этого заказа.')
    )
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Цена'),
        help_text=_('Цена этого заказа.')
    )
    address = models.CharField(
        max_length=120,
        verbose_name=_('Адрес'),
        help_text=_('Адрес доставки для этого заказа.')
    )
    description = models.TextField(
        max_length=10000,
        null=True,
        blank=True,
        verbose_name=_('Описание'),
        help_text=_('Дополнительное описание или комментарии к этому заказу.')
    )

    class Meta:
        ordering = ['-creation_time']
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')

    def clean(self):
        super().clean()
        if self.contact_number:
            try:
                parsed_number = phonenumbers.parse(self.contact_number, None)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise ValidationError(_("Неверный формат номера телефона."))
            except phonenumbers.NumberParseException:
                raise ValidationError(_("Неверный формат номера телефона."))

    def save(self, *args, **kwargs):
        if self.contact_number:
            parsed_number = phonenumbers.parse(self.contact_number, None)
            formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            self.contact_number = formatted_number
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
