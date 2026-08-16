from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .device_model import DeviceModel
from .common import OperatingSystem, MIN_YEAR, CURRENT_YEAR, Protocol


class Device(models.Model):
    device_model = models.ForeignKey(
        DeviceModel,
        on_delete=models.CASCADE,
        related_name="devices",
        verbose_name=_("Модель устройства"),
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Серийный номер"),
        help_text=_("Уникален в рамках модели устройства"),
    )
    inventory_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Инвентарный номер"),
        help_text=_("Глобально уникален"),
    )
    operating_system = models.ForeignKey(
        OperatingSystem,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="devices",
        verbose_name=_("Операционная система"),
    )
    purchase_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(MIN_YEAR),
            MaxValueValidator(CURRENT_YEAR + 1),
        ],
        verbose_name=_("Год приобретения"),
        help_text=_("Год приобретения устройства"),
    )

    """
    далее должно ссылаться на модель ip адреса с помощью Many to many
    или будет модель интерфейс
    """
    management_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
    )

    management_protocols = models.ManyToManyField(
        Protocol,
        blank=True,
        related_name="devices",
        verbose_name=_("Протоколы управления"),
    )

    class Meta:
        verbose_name = _("Устройство")
        verbose_name_plural = _("Устройства")
        constraints = [
            models.UniqueConstraint(
                fields=["device_model", "serial_number"],
                condition=(
                        ~Q(serial_number=None)
                        & ~Q(serial_number="")
                ),
                name="device_serial_number_unique_per_model",
            ),
            models.UniqueConstraint(
                fields=["inventory_number"],
                condition=(
                        ~Q(inventory_number=None)
                        & ~Q(inventory_number="")
                ),
                name="device_inventory_number_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["serial_number"],
                name="device_serial_number_idx",
            ),
            models.Index(
                fields=["management_ip"],
                name="device_management_ip_idx",
            ),
            models.Index(
                fields=["purchase_year"],
                name="device_purchase_year_idx",
            ),
        ]

    def __str__(self):
        identifier = (
                self.serial_number
                or self.inventory_number
                or f"id={self.pk}"
        )
        return f"{self.device_model} {identifier}"
